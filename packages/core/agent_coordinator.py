"""
Agent Coordinator for Multi-Agent System
Implements weighted voting and decision logic (L:VI - Centralized coordination)
"""

import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from packages.core.multi_agent import AgentInterface, AgentResult
from packages.core.agent_registry import AgentRegistry


class CoordinatorDecision(BaseModel):
    """Coordinator's final decision with token usage"""
    final_prompt: str
    selected_agent: str
    decision_rationale: str
    agent_results: List[AgentResult]
    vote_breakdown: Dict[str, float]
    token_usage: Optional[Dict[str, Any]] = None  # Aggregated token usage across all agents
    total_cost_usd: Optional[float] = None  # Total cost in USD
    total_tokens: Optional[int] = None  # Total tokens used


class AgentCoordinator:
    """
    Coordinates multiple agents and merges their outputs.
    Follows centralized coordination pattern (L:VI).
    """
    
    def __init__(self, agent_names: Optional[List[str]] = None, weights: Optional[Dict[str, float]] = None):
        """
        Initialize coordinator with agents from registry.
        
        Args:
            agent_names: List of agent names to use (default: all registered)
            weights: Optional weights per agent (default: equal weights)
        """
        # Create agents from registry
        if agent_names:
            self.agents = [AgentRegistry.create_agent(name) for name in agent_names]
        else:
            self.agents = AgentRegistry.create_default_agents()
        
        # Set weights (default: equal weights)
        self.weights = weights or {agent.name: 1.0 for agent in self.agents}
    
    async def coordinate(self, prompt: str) -> CoordinatorDecision:
        """
        Run all agents in parallel and merge results.
        Follows L:IV atomicity (parallel execution with asyncio.gather).
        
        Args:
            prompt: Prompt text to optimize
        
        Returns:
            CoordinatorDecision with final prompt and metadata
        """
        # Execute agents in parallel (L:IV atomicity)
        tasks = [agent.run(prompt) for agent in self.agents]
        results = await asyncio.gather(*tasks)
        
        # Aggregate token usage from all agents
        token_usage_by_agent = {}
        total_cost = 0.0
        total_tokens = 0
        
        for result in results:
            if result.token_usage:
                token_usage_by_agent[result.agent_name] = result.token_usage
                total_cost += result.token_usage.get("cost_usd", 0.0)
                total_tokens += result.token_usage.get("total_tokens", 0)
        
        # Weighted voting: Calculate scores
        weighted_scores = {}
        for result in results:
            # Base score = analysis score * confidence
            base_score = result.analysis.score * result.suggestions.confidence
            # Apply agent weight
            weighted_scores[result.agent_name] = base_score * self.weights[result.agent_name]
        
        # Select winner (highest weighted score)
        winner_name = max(weighted_scores, key=weighted_scores.get)
        winner_result = next(r for r in results if r.agent_name == winner_name)
        
        # Build decision rationale
        rationale = (
            f"Selected {winner_name} (weighted score: {weighted_scores[winner_name]:.2f}). "
            f"Analysis score: {winner_result.analysis.score:.1f}/10, "
            f"Confidence: {winner_result.suggestions.confidence:.0%}"
        )
        
        return CoordinatorDecision(
            final_prompt=winner_result.suggestions.improved_prompt,
            selected_agent=winner_name,
            decision_rationale=rationale,
            agent_results=results,
            vote_breakdown=weighted_scores,
            token_usage=token_usage_by_agent if token_usage_by_agent else None,
            total_cost_usd=total_cost if total_cost > 0 else None,
            total_tokens=total_tokens if total_tokens > 0 else None
        )
    
    def get_agent_names(self) -> List[str]:
        """
        Get list of active agent names.
        
        Returns:
            List of agent names
        """
        return [agent.name for agent in self.agents]
    
    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """
        Update agent weights.
        
        Args:
            new_weights: Dictionary of agent_name -> weight
        """
        self.weights.update(new_weights)

