import pytest
import json
import tempfile
import os
from pathlib import Path
from llx.pricing_manager import PricingManager


class TestPricingManager:
    """Test the PricingManager class"""

    def test_pricing_manager_init_with_default_file(self):
        # Test initialization with default pricing file
        manager = PricingManager()
        assert manager._pricing_data is not None
        assert "pricing" in manager._pricing_data
        assert "defaults" in manager._pricing_data
        assert "free_providers" in manager._pricing_data

    def test_pricing_manager_init_with_custom_file(self):
        # Create a temporary pricing file
        test_pricing = {
            "pricing": {
                "test:model": {
                    "input": 0.001,
                    "output": 0.002,
                    "currency": "USD",
                    "per_tokens": 1000
                }
            },
            "defaults": {
                "input": 0.01,
                "output": 0.02,
                "currency": "USD",
                "per_tokens": 1000
            },
            "free_providers": ["local"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_pricing, f)
            temp_file = f.name
        
        try:
            manager = PricingManager(temp_file)
            assert manager._pricing_data == test_pricing
        finally:
            os.unlink(temp_file)

    def test_get_model_pricing_exact_match(self):
        manager = PricingManager()
        
        # Test getting pricing for a model that exists
        pricing = manager.get_model_pricing("openai:gpt-4")
        assert pricing["input"] == 0.03
        assert pricing["output"] == 0.06

    def test_get_model_pricing_free_provider(self):
        manager = PricingManager()
        
        # Test free provider
        pricing = manager.get_model_pricing("ollama:llama3.2")
        assert pricing["input"] == 0.0
        assert pricing["output"] == 0.0

    def test_get_model_pricing_fallback_to_defaults(self):
        manager = PricingManager()
        
        # Test model that doesn't exist - should fall back to defaults
        pricing = manager.get_model_pricing("unknown:model")
        assert pricing["input"] == 0.01  # Default value
        assert pricing["output"] == 0.02  # Default value

    def test_calculate_cost(self):
        manager = PricingManager()
        
        # Test cost calculation for known model
        cost = manager.calculate_cost("openai:gpt-4", 1000, 1000)
        expected = (1000/1000 * 0.03) + (1000/1000 * 0.06)  # $0.09
        assert cost == 0.09
        
        # Test cost calculation for free provider
        cost = manager.calculate_cost("ollama:llama3.2", 1000, 1000)
        assert cost == 0.0

    def test_is_free_provider(self):
        manager = PricingManager()
        
        assert manager.is_free_provider("ollama:llama3.2") == True
        assert manager.is_free_provider("openai:gpt-4") == False

    def test_add_model_pricing(self):
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "pricing": {},
                "defaults": {"input": 0.01, "output": 0.02, "currency": "USD", "per_tokens": 1000},
                "free_providers": []
            }, f)
            temp_file = f.name
        
        try:
            manager = PricingManager(temp_file)
            
            # Add new model pricing
            manager.add_model_pricing("test:model", 0.005, 0.010, save=False)
            
            # Verify it was added
            pricing = manager.get_model_pricing("test:model")
            assert pricing["input"] == 0.005
            assert pricing["output"] == 0.010
            
            # Test cost calculation with new pricing
            cost = manager.calculate_cost("test:model", 1000, 1000)
            expected = (1000/1000 * 0.005) + (1000/1000 * 0.010)  # $0.015
            assert cost == 0.015
        finally:
            os.unlink(temp_file)

    def test_get_all_models(self):
        manager = PricingManager()
        
        models = manager.get_all_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert "openai:gpt-4" in models

    def test_fallback_when_file_missing(self):
        # Test with non-existent file
        manager = PricingManager("/non/existent/file.json")
        
        # Should still work with defaults
        assert manager._pricing_data is not None
        pricing = manager.get_model_pricing("any:model")
        assert pricing["input"] == 0.01  # Default fallback
        assert pricing["output"] == 0.02  # Default fallback