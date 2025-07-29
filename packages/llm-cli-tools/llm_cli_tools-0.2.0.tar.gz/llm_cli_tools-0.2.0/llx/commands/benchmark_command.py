import asyncio
import click
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from abc import ABC
from llx.utils import get_provider
from llx.pricing_manager import get_pricing_manager
from llx.response_judge import ResponseJudge


class BenchmarkRunner:
    """Handle benchmark execution across multiple models"""
    
    def __init__(self, models: List[str]):
        self.models = models
        self.providers = {}
        self.pricing_manager = get_pricing_manager()
        
        # Initialize providers for each model
        for model in models:
            provider_name, model_name = model.split(':', 1)
            self.providers[model] = get_provider(provider_name, model_name)
    
    async def run_prompt(self, prompt: str) -> Dict[str, Any]:
        """Run a single prompt across all models and collect metrics"""
        results = {}
        
        for model in self.models:
            try:
                click.echo(f"  ⏳ Testing {model}...", nl=False)
                start_time = time.time()
                
                # Execute the prompt with usage data
                response_text, usage_data = await self.providers[model].invoke_with_usage(prompt)
                
                end_time = time.time()
                response_time = end_time - start_time
                click.echo(f" ✅ ({response_time:.1f}s)")
                
                # Use actual usage data or fallback to estimation
                input_tokens = usage_data.input_tokens or self._estimate_tokens(prompt)
                output_tokens = usage_data.output_tokens or self._estimate_tokens(response_text)
                total_tokens = usage_data.total_tokens or (input_tokens + output_tokens)
                
                # Calculate cost using dynamic pricing
                estimated_cost = self.pricing_manager.calculate_cost(model, input_tokens, output_tokens)
                
                results[model] = {
                    "response": response_text,
                    "response_time": round(response_time, 2),
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost": estimated_cost,
                    "status": "success"
                }
                
            except Exception as e:
                click.echo(f" ❌ Error")
                results[model] = {
                    "response": "",
                    "response_time": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "estimated_cost": 0,
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def _estimate_tokens(self, text: str) -> int:
        """Simple token estimation fallback (roughly 4 chars per token)"""
        return max(1, len(text) // 4)


class BenchmarkCommand(ABC):
    """Handle the benchmark command logic"""
    
    def __init__(self):
        self.results = []
    
    def execute(self, prompt: str, models: List[str], output_format: str = "table", 
               output_file: Optional[str] = None, judge_model: Optional[str] = None,
               judge_prompt: Optional[str] = None, comparative: bool = False):
        """Execute benchmark across models"""
        
        click.echo(click.style("🚀 Starting benchmark...", fg='cyan', bold=True))
        click.echo(f"Prompt: {click.style(prompt, fg='yellow')}")
        click.echo(f"Models: {click.style(', '.join(models), fg='green')}")
        if judge_model:
            judge_mode = "comparative" if comparative else "individual"
            click.echo(f"Judge: {click.style(judge_model, fg='magenta')} ({judge_mode})")
        click.echo()
        
        runner = BenchmarkRunner(models)
        
        # Run the benchmark
        try:
            results = asyncio.run(runner.run_prompt(prompt))
            
            # Run judging if judge model is specified
            judgments = {}
            comparative_result = {}
            if judge_model:
                click.echo(click.style("🧠 Running response evaluation...", fg='cyan', bold=True))
                judge = ResponseJudge(judge_model, judge_prompt)
                
                # Extract responses for judging
                responses = {
                    model: result["response"] 
                    for model, result in results.items() 
                    if result["status"] == "success"
                }
                
                if responses:
                    if comparative:
                        # Run comparative judging
                        comparative_result = asyncio.run(judge.comparative_judge(prompt, responses))
                        click.echo(click.style("✅ Comparative evaluation complete!", fg='green'))
                    else:
                        # Run individual judging
                        judgments = asyncio.run(judge.judge_multiple_responses(prompt, responses))
                        click.echo(click.style("✅ Individual evaluation complete!", fg='green'))
                else:
                    click.echo(click.style("⚠️  No successful responses to judge", fg='yellow'))
            
            benchmark_data = {
                "benchmark_id": f"bench_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "models": models,
                "judge_model": judge_model,
                "comparative_mode": comparative,
                "results": results,
                "judgments": judgments,
                "comparative_result": comparative_result
            }
            
            # Output results
            if output_format == "json":
                self._output_json(benchmark_data, output_file)
            else:
                self._output_table(benchmark_data)
            
            # Save to file if specified
            if output_file and output_format != "json":
                self._save_to_file(benchmark_data, output_file)
                
        except Exception as e:
            click.echo(click.style(f"❌ Benchmark failed: {str(e)}", fg='red'))
    
    def _output_table(self, data: Dict[str, Any]):
        """Output results in table format"""
        click.echo(click.style("📊 Benchmark Results", fg='cyan', bold=True))
        
        # Check if we have judgments or comparative results
        has_judgments = bool(data.get("judgments"))
        has_comparative = bool(data.get("comparative_result"))
        table_width = 120 if (has_judgments or has_comparative) else 100
        
        click.echo("=" * table_width)
        
        # Header
        if has_judgments or has_comparative:
            if has_comparative:
                header = f"{'Model':<25} {'Status':<10} {'Time (s)':<10} {'Tokens':<10} {'Cost ($)':<12} {'Rank':<8} {'Response Preview':<30}"
            else:
                header = f"{'Model':<25} {'Status':<10} {'Time (s)':<10} {'Tokens':<10} {'Cost ($)':<12} {'Score':<8} {'Response Preview':<30}"
        else:
            header = f"{'Model':<25} {'Status':<10} {'Time (s)':<10} {'Tokens':<10} {'Cost ($)':<12} {'Response Preview':<30}"
        
        click.echo(click.style(header, fg='blue', bold=True))
        click.echo("-" * table_width)
        
        # Results
        for model, result in data["results"].items():
            status = "✅ OK" if result["status"] == "success" else "❌ ERROR"
            time_str = f"{result['response_time']:.2f}" if result["status"] == "success" else "N/A"
            tokens_str = str(result['total_tokens']) if result["status"] == "success" else "N/A"
            cost_str = f"{result['estimated_cost']:.6f}" if result["status"] == "success" else "N/A"
            
            # Get judgment score or ranking if available
            score_str = "N/A"
            if has_comparative and data.get("comparative_result"):
                comp_result = data["comparative_result"]
                if comp_result.get("status") == "success" and comp_result.get("ranking"):
                    ranking = comp_result["ranking"]
                    if model in ranking:
                        rank = ranking.index(model) + 1
                        score_str = f"#{rank}"
                        if model == comp_result.get("winner"):
                            score_str += " 🏆"
            elif has_judgments and model in data["judgments"]:
                judgment = data["judgments"][model]
                if judgment.get("status") == "success" and judgment.get("score"):
                    score_str = f"{judgment['score']:.1f}/10"
            
            # Preview first 30 chars of response
            preview = result.get('response', '')[:27] + "..." if len(result.get('response', '')) > 30 else result.get('response', '')
            if result["status"] == "error":
                preview = f"Error: {result.get('error', 'Unknown error')}"[:30]
            
            if has_judgments or has_comparative:
                row = f"{model:<25} {status:<10} {time_str:<10} {tokens_str:<10} {cost_str:<12} {score_str:<8} {preview:<30}"
            else:
                row = f"{model:<25} {status:<10} {time_str:<10} {tokens_str:<10} {cost_str:<12} {preview:<30}"
            
            click.echo(row)
        
        click.echo("-" * table_width)
        
        # Summary
        successful_results = [r for r in data["results"].values() if r["status"] == "success"]
        if successful_results:
            avg_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
            total_cost = sum(r["estimated_cost"] for r in successful_results)
            
            click.echo(click.style(f"📈 Summary:", fg='green', bold=True))
            click.echo(f"   Average response time: {avg_time:.2f}s")
            click.echo(f"   Total estimated cost: ${total_cost:.6f}")
            click.echo(f"   Successful responses: {len(successful_results)}/{len(data['results'])}")
            
            # Judgment summary
            if has_comparative and data.get("comparative_result"):
                comp_result = data["comparative_result"]
                if comp_result.get("status") == "success":
                    winner = comp_result.get("winner")
                    ranking = comp_result.get("ranking", [])
                    if winner and ranking:
                        click.echo(f"   Winner: {winner}")
                        click.echo(f"   Full ranking: {' > '.join(ranking)}")
            elif has_judgments:
                successful_judgments = [
                    j for j in data["judgments"].values() 
                    if j.get("status") == "success" and j.get("score")
                ]
                if successful_judgments:
                    avg_score = sum(j["score"] for j in successful_judgments) / len(successful_judgments)
                    best_score = max(j["score"] for j in successful_judgments)
                    click.echo(f"   Average quality score: {avg_score:.1f}/10")
                    click.echo(f"   Best quality score: {best_score:.1f}/10")
        
        # Show detailed judgments if available
        if has_comparative and data.get("comparative_result"):
            comp_result = data["comparative_result"]
            if comp_result.get("status") == "success":
                click.echo()
                click.echo(click.style("🏆 Comparative Analysis:", fg='magenta', bold=True))
                click.echo("-" * 80)
                
                comparison = comp_result.get("comparison", "No comparison provided")
                click.echo(f"Comparison: {comparison}")
                click.echo()
                
                # Show ranking with scores
                ranking = comp_result.get("ranking", [])
                scores = comp_result.get("scores", {})
                for i, model in enumerate(ranking, 1):
                    score = scores.get(model, "N/A")
                    trophy = "🏆 " if i == 1 else f"{i}. "
                    click.echo(f"{trophy}{model}: {score}/10")
                click.echo()
                
                # Show strengths and weaknesses
                strengths = comp_result.get("strengths", {})
                weaknesses = comp_result.get("weaknesses", {})
                for model in ranking:
                    click.echo(click.style(f"{model}:", fg='blue', bold=True))
                    if model in strengths and strengths[model]:
                        click.echo(f"  Strengths: {', '.join(strengths[model])}")
                    if model in weaknesses and weaknesses[model]:
                        click.echo(f"  Weaknesses: {', '.join(weaknesses[model])}")
                    click.echo()
        elif has_judgments and data["judgments"]:
            click.echo()
            click.echo(click.style("🧠 Detailed Evaluations:", fg='magenta', bold=True))
            click.echo("-" * 80)
            
            for model, judgment in data["judgments"].items():
                if judgment.get("status") == "success":
                    score = judgment.get("score", "N/A")
                    reasoning = judgment.get("reasoning", "No reasoning provided")
                    
                    click.echo(click.style(f"{model}:", fg='blue', bold=True) + f" {score}/10")
                    click.echo(f"  Reasoning: {reasoning}")
                    
                    strengths = judgment.get("strengths", [])
                    if strengths:
                        click.echo(f"  Strengths: {', '.join(strengths)}")
                    
                    weaknesses = judgment.get("weaknesses", [])
                    if weaknesses:
                        click.echo(f"  Weaknesses: {', '.join(weaknesses)}")
                    
                    click.echo()
                else:
                    click.echo(click.style(f"{model}:", fg='red', bold=True) + f" Judgment failed")
                    click.echo(f"  Error: {judgment.get('error', 'Unknown error')}")
                    click.echo()
    
    def _output_json(self, data: Dict[str, Any], output_file: Optional[str] = None):
        """Output results in JSON format"""
        json_output = json.dumps(data, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_output)
            click.echo(click.style(f"📁 Results saved to: {output_file}", fg='green'))
        else:
            click.echo(json_output)
    
    def _save_to_file(self, data: Dict[str, Any], filename: str):
        """Save benchmark results to file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        click.echo(click.style(f"📁 Results saved to: {filename}", fg='green'))