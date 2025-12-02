import tiktoken
from typing import Dict
from pydantic import BaseModel
from datetime import datetime

# Groq pricing (verified 2025-11-06)
GROQ_PRICING = {
    "llama-3.3-70b-versatile": {
        "input": 0.00000059,   # $0.59 per 1M tokens
        "output": 0.00000079,  # $0.79 per 1M tokens
    }
}

class TokenUsage(BaseModel):
    """Token usage for single LLM call"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    timestamp: datetime
    cost_usd: float

class ComparisonMetrics(BaseModel):
    """Comparison metrics between original and improved"""
    # Original execution
    original_prompt_tokens: int
    original_output_tokens: int
    original_total_tokens: int
    original_cost_usd: float
    
    # Improved execution
    improved_prompt_tokens: int
    improved_output_tokens: int
    improved_total_tokens: int
    improved_cost_usd: float
    
    # Process overhead
    improvement_process_tokens: int
    improvement_process_cost_usd: float
    judging_tokens: int
    judging_cost_usd: float
    
    # Totals
    total_tokens_used: int
    total_cost_usd: float
    
    # Efficiency metrics
    token_difference: int
    token_efficiency_percent: float
    output_quality_improvement: float
    cost_per_quality_point: float
    is_worth_it: bool
    roi_score: float

class TokenTracker:
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        pricing = GROQ_PRICING.get(model, GROQ_PRICING["llama-3.3-70b-versatile"])
        return (prompt_tokens * pricing["input"]) + (completion_tokens * pricing["output"])
    
    def track_llm_call(self, prompt: str, completion: str, model: str = "llama-3.3-70b-versatile") -> TokenUsage:
        prompt_tokens = self.count_tokens(prompt)
        completion_tokens = self.count_tokens(completion)
        cost = self.calculate_cost(prompt_tokens, completion_tokens, model)
        
        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=model,
            timestamp=datetime.now(),
            cost_usd=cost
        )
    
    def compare_executions(
        self,
        original_prompt: str,
        original_output: str,
        improved_prompt: str,
        improved_output: str,
        improvement_tokens: int,
        improvement_cost: float,
        judging_tokens: int,
        judging_cost: float,
        quality_improvement: float,
        model: str = "llama-3.3-70b-versatile"
    ) -> ComparisonMetrics:
        # Calculate original
        orig_prompt_tok = self.count_tokens(original_prompt)
        orig_output_tok = self.count_tokens(original_output)
        orig_cost = self.calculate_cost(orig_prompt_tok, orig_output_tok, model)
        
        # Calculate improved
        imp_prompt_tok = self.count_tokens(improved_prompt)
        imp_output_tok = self.count_tokens(improved_output)
        imp_cost = self.calculate_cost(imp_prompt_tok, imp_output_tok, model)
        
        # Totals
        total_tokens = (orig_prompt_tok + orig_output_tok + imp_prompt_tok +
                       imp_output_tok + improvement_tokens + judging_tokens)
        total_cost = orig_cost + imp_cost + improvement_cost + judging_cost
        
        # Efficiency
        token_diff = imp_output_tok - orig_output_tok
        token_eff = ((imp_output_tok / orig_output_tok) - 1) * 100 if orig_output_tok > 0 else 0
        cost_per_quality = (imp_cost - orig_cost) / quality_improvement if quality_improvement > 0 else float('inf')
        
        # ROI
        cost_increase = ((imp_cost - orig_cost) / orig_cost) * 100 if orig_cost > 0 else 0
        is_worth_it = quality_improvement > 5.0 and cost_increase < 100
        roi_score = quality_improvement / ((imp_cost - orig_cost) * 1000000) if imp_cost > orig_cost else float('inf')
        
        return ComparisonMetrics(
            original_prompt_tokens=orig_prompt_tok,
            original_output_tokens=orig_output_tok,
            original_total_tokens=orig_prompt_tok + orig_output_tok,
            original_cost_usd=orig_cost,
            improved_prompt_tokens=imp_prompt_tok,
            improved_output_tokens=imp_output_tok,
            improved_total_tokens=imp_prompt_tok + imp_output_tok,
            improved_cost_usd=imp_cost,
            improvement_process_tokens=improvement_tokens,
            improvement_process_cost_usd=improvement_cost,
            judging_tokens=judging_tokens,
            judging_cost_usd=judging_cost,
            total_tokens_used=total_tokens,
            total_cost_usd=total_cost,
            token_difference=token_diff,
            token_efficiency_percent=token_eff,
            output_quality_improvement=quality_improvement,
            cost_per_quality_point=cost_per_quality,
            is_worth_it=is_worth_it,
            roi_score=roi_score
        )