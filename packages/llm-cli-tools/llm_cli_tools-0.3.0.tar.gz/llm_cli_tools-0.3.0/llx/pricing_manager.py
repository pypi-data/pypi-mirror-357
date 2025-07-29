import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class PricingManager:
    """Manage model pricing data from external configuration"""
    
    def __init__(self, pricing_file: Optional[str] = None):
        if pricing_file is None:
            # Default to pricing.json in the same directory as this file
            pricing_file = Path(__file__).parent / "pricing.json"
        
        self.pricing_file = pricing_file
        self._pricing_data = None
        self._load_pricing_data()
    
    def _load_pricing_data(self):
        """Load pricing data from JSON file"""
        try:
            with open(self.pricing_file, 'r') as f:
                self._pricing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Fallback to basic pricing if file is missing or invalid
            self._pricing_data = {
                "pricing": {},
                "defaults": {
                    "input": 0.01,
                    "output": 0.02,
                    "currency": "USD",
                    "per_tokens": 1000
                },
                "free_providers": ["ollama"]
            }
    
    def get_model_pricing(self, model: str) -> Dict[str, Any]:
        """Get pricing for a specific model"""
        # Check if provider is free
        provider = model.split(':')[0]
        if provider in self._pricing_data.get("free_providers", []):
            return {
                "input": 0.0,
                "output": 0.0,
                "currency": "USD",
                "per_tokens": 1000
            }
        
        # Look for exact model match
        pricing = self._pricing_data["pricing"].get(model)
        if pricing:
            return pricing
        
        # Look for provider default (e.g., "openai:gpt-4" -> "openai")
        provider_default = f"{provider}:default"
        pricing = self._pricing_data["pricing"].get(provider_default)
        if pricing:
            return pricing
        
        # Use global defaults
        return self._pricing_data["defaults"]
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a model based on token usage"""
        pricing = self.get_model_pricing(model)
        
        per_tokens = pricing.get("per_tokens", 1000)
        input_cost = (input_tokens / per_tokens) * pricing.get("input", 0)
        output_cost = (output_tokens / per_tokens) * pricing.get("output", 0)
        
        return round(input_cost + output_cost, 6)
    
    def is_free_provider(self, model: str) -> bool:
        """Check if a provider is free"""
        provider = model.split(':')[0]
        return provider in self._pricing_data.get("free_providers", [])
    
    def reload_pricing(self):
        """Reload pricing data from file"""
        self._load_pricing_data()
    
    def get_all_models(self) -> list:
        """Get list of all models with pricing data"""
        return list(self._pricing_data["pricing"].keys())
    
    def add_model_pricing(self, model: str, input_price: float, output_price: float, save: bool = True):
        """Add or update pricing for a model"""
        self._pricing_data["pricing"][model] = {
            "input": input_price,
            "output": output_price,
            "currency": "USD",
            "per_tokens": 1000,
            "last_updated": "user_added"
        }
        
        if save:
            self.save_pricing()
    
    def save_pricing(self):
        """Save current pricing data to file"""
        try:
            with open(self.pricing_file, 'w') as f:
                json.dump(self._pricing_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save pricing data: {e}")


# Global pricing manager instance
_pricing_manager = None

def get_pricing_manager() -> PricingManager:
    """Get the global pricing manager instance"""
    global _pricing_manager
    if _pricing_manager is None:
        _pricing_manager = PricingManager()
    return _pricing_manager