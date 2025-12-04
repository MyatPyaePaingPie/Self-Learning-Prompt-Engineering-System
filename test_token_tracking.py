"""
Test script for token tracking in multi-agent system
Run this to verify token usage and cost calculations are working
"""

import asyncio
import os
from packages.core.agent_coordinator import AgentCoordinator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_token_tracking():
    print("=" * 60)
    print("Multi-Agent Token Tracking Test")
    print("=" * 60)
    
    # Test prompt
    test_prompt = "Write a Python function to calculate the fibonacci sequence"
    
    print(f"\nTest Prompt: {test_prompt}\n")
    
    # Create coordinator with default agents
    coordinator = AgentCoordinator()
    
    print("Running multi-agent optimization...")
    print("-" * 60)
    
    # Run coordination
    decision = await coordinator.coordinate(test_prompt)
    
    # Display results
    print(f"\n✅ Winner: {decision.selected_agent}")
    print(f"📝 Rationale: {decision.decision_rationale}")
    
    # Display token usage
    print("\n" + "=" * 60)
    print("TOKEN USAGE & COST ANALYSIS")
    print("=" * 60)
    
    if decision.token_usage:
        print("\nPer-Agent Breakdown:")
        print("-" * 60)
        for agent_name, usage in decision.token_usage.items():
            print(f"\n{agent_name.upper()} Agent:")
            print(f"  Model: {usage.get('model', 'N/A')}")
            print(f"  Prompt Tokens: {usage.get('prompt_tokens', 0):,}")
            print(f"  Completion Tokens: {usage.get('completion_tokens', 0):,}")
            print(f"  Total Tokens: {usage.get('total_tokens', 0):,}")
            print(f"  Cost: ${usage.get('cost_usd', 0):.6f}")
    
    # Display totals
    print("\n" + "=" * 60)
    print("TOTAL COSTS")
    print("=" * 60)
    print(f"Total Tokens: {decision.total_tokens:,}" if decision.total_tokens else "Total Tokens: N/A")
    print(f"Total Cost: ${decision.total_cost_usd:.6f}" if decision.total_cost_usd else "Total Cost: N/A")
    
    # Cost comparison
    if decision.total_cost_usd:
        print("\n" + "=" * 60)
        print("COST COMPARISON")
        print("=" * 60)
        
        # Calculate what it would cost with all 70B models
        syntax_tokens = decision.token_usage.get("syntax", {}).get("total_tokens", 0)
        structure_tokens = decision.token_usage.get("structure", {}).get("total_tokens", 0)
        domain_tokens = decision.token_usage.get("domain", {}).get("total_tokens", 0)
        
        # 70B model pricing (approximation: $0.59 input + $0.79 output, assume 50/50 split)
        avg_70b_price_per_token = (0.00000059 + 0.00000079) / 2
        all_70b_cost = (syntax_tokens + structure_tokens + domain_tokens) * avg_70b_price_per_token
        
        savings = all_70b_cost - decision.total_cost_usd
        savings_percent = (savings / all_70b_cost * 100) if all_70b_cost > 0 else 0
        
        print(f"All 70B Models Cost: ${all_70b_cost:.6f}")
        print(f"Optimized Cost: ${decision.total_cost_usd:.6f}")
        print(f"Savings: ${savings:.6f} ({savings_percent:.1f}%)")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_token_tracking())

