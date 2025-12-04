#!/usr/bin/env python3
"""
Test Data Generator for Agent Effectiveness Dashboard
Creates synthetic multi-agent data so the dashboard has something to display.
"""

import sys
from pathlib import Path
import uuid
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.db.session import get_session
from packages.db.models import Prompt, PromptVersion, JudgeScore, BestHead
import random

def generate_test_data(num_prompts=10):
    """
    Generate synthetic multi-agent data for testing.
    
    Creates:
    - Prompts with multiple versions (syntax, structure, domain agents)
    - Judge scores for each version
    - Best head tracking
    """
    # Get session from context manager
    from contextlib import contextmanager
    session_gen = get_session()
    session = session_gen.__enter__()
    
    print("🎲 Generating synthetic multi-agent data...")
    
    agent_sources = ['syntax', 'structure', 'domain']
    sample_prompts = [
        "Write a Python function to sort a list",
        "Explain quantum computing in simple terms",
        "Create a REST API endpoint for user authentication",
        "Design a database schema for an e-commerce site",
        "Implement a binary search tree in JavaScript",
        "Write a regex pattern to validate email addresses",
        "Create a responsive navigation menu with CSS",
        "Explain the difference between SQL and NoSQL",
        "Implement merge sort algorithm with comments",
        "Design a microservices architecture"
    ]
    
    try:
        for i in range(num_prompts):
            # Create prompt
            prompt = Prompt(
                user_id="test_user",
                original_text=sample_prompts[i % len(sample_prompts)]
            )
            session.add(prompt)
            session.flush()
            
            print(f"  Creating prompt {i+1}/{num_prompts}: {prompt.original_text[:50]}...")
            
            # Create versions for each agent
            versions = []
            for j, agent in enumerate(agent_sources):
                version = PromptVersion(
                    prompt_id=prompt.id,
                    version_no=j + 1,
                    text=f"{prompt.original_text} [Enhanced by {agent} agent]",
                    explanation={"agent": agent, "improvements": ["clarity", "structure"]},
                    source=agent
                )
                session.add(version)
                session.flush()
                versions.append(version)
                
                # Create judge scores (random but biased)
                # Structure agent tends to score higher
                base_scores = {
                    'syntax': [7.0, 8.0, 7.5, 8.0, 7.0],
                    'structure': [8.5, 9.0, 8.5, 9.0, 8.0],  # Best performer
                    'domain': [7.5, 8.0, 7.0, 8.0, 7.5]
                }
                
                scores = base_scores[agent]
                scores = [s + random.uniform(-0.5, 0.5) for s in scores]  # Add variance
                
                judge_score = JudgeScore(
                    prompt_version_id=version.id,
                    clarity=scores[0],
                    specificity=scores[1],
                    actionability=scores[2],
                    structure=scores[3],
                    context_use=scores[4],
                    feedback={"synthetic": True, "agent": agent}
                )
                session.add(judge_score)
            
            # Pick best version (structure agent wins most often)
            best_version = random.choice(versions)
            # 60% chance structure agent wins
            if random.random() < 0.6:
                best_version = next((v for v in versions if v.source == 'structure'), versions[0])
            
            best_head = BestHead(
                prompt_id=prompt.id,
                prompt_version_id=best_version.id,
                score=40.0  # Sum of 5 scores around 8.0 each
            )
            session.add(best_head)
        
        session.commit()
        print(f"\n✅ Generated {num_prompts} prompts with multi-agent versions!")
        print(f"   Total versions created: {num_prompts * 3}")
        print(f"   Agent distribution: {len(agent_sources)} agents per prompt")
        print(f"\n🎯 Expected effectiveness (approximate):")
        print(f"   - Structure: ~60% win rate (best performer)")
        print(f"   - Syntax: ~20% win rate")
        print(f"   - Domain: ~20% win rate")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error generating data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate test data for agent effectiveness")
    parser.add_argument('--prompts', type=int, default=10, help='Number of prompts to generate')
    args = parser.parse_args()
    
    generate_test_data(args.prompts)

