#!/usr/bin/env python3
"""
Temporal Data Generator for Self-Learning Prompt Engineering System
Week 12: Temporal Prompt Learning & Causal Analysis
Author: Atang's Assignment

This module generates synthetic prompt version history for testing temporal analysis.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
import random
import difflib


def generate_synthetic_history(
    prompt_id: str,
    days: int = 30,
    versions_per_day: int = 2
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generate synthetic prompt version history with temporal patterns.
    
    Args:
        prompt_id: UUID of the prompt
        days: Number of days of history (default 30)
        versions_per_day: Versions per day (default 2)
        
    Returns:
        Tuple of (versions, edges):
        - versions: List of VersionNode dicts
        - edges: List of CausalEdge dicts
    """
    total_versions = days * versions_per_day
    versions = []
    edges = []
    
    # Base prompt text
    base_text = "Write a Python function to calculate fibonacci numbers"
    
    # Choose trend type (improving, degrading, oscillating)
    trend_type = random.choice(["improving", "degrading", "oscillating"])
    
    # Generate versions
    previous_version_id = None
    previous_text = base_text
    previous_score = 60.0  # Starting score
    
    change_types = ["structure", "wording", "length", "other"]
    
    for day in range(days):
        for version_num in range(versions_per_day):
            # Calculate timestamp (spread across days)
            hours_offset = day * 24 + (version_num * 24 / versions_per_day)
            version_date = datetime.utcnow() - timedelta(days=days - day) + timedelta(hours=hours_offset)
            
            # Generate version text (progressive modification)
            version_count = day * versions_per_day + version_num
            if version_count % 5 == 0:
                # Major rewrite every 5 versions
                version_text = f"{base_text} with error handling and docstring [v{version_count + 1}]"
            elif version_count % 3 == 0:
                # Length change every 3 versions
                version_text = f"{previous_text}\\nAdditional requirements: efficient implementation"
            else:
                # Minor wording changes
                version_text = previous_text.replace("Python", f"Python{version_count + 1}")
            
            # Compute change type and magnitude
            change_type = _compute_change_type(previous_text, version_text)
            change_magnitude = _compute_change_magnitude(previous_text, version_text)
            
            # Generate score based on trend type
            if trend_type == "improving":
                # Linear improvement with noise
                score = previous_score + random.uniform(0.5, 2.0) + random.uniform(-1, 1)
            elif trend_type == "degrading":
                # Linear degradation with noise
                score = previous_score - random.uniform(0.5, 2.0) + random.uniform(-1, 1)
            else:  # oscillating
                # Sinusoidal pattern with noise
                score = 70 + 10 * (1 if version_count % 4 < 2 else -1) + random.uniform(-2, 2)
            
            # Clamp score to 0-100
            score = max(0, min(100, score))
            
            # Create version
            version_id = str(uuid.uuid4())
            version = {
                "version_id": version_id,
                "parent_version_id": previous_version_id,
                "timestamp": version_date.isoformat(),
                "text": version_text,
                "score": score,
                "change_type": change_type,
                "change_magnitude": change_magnitude
            }
            versions.append(version)
            
            # Create causal edge (parent → child transition)
            if previous_version_id:
                score_delta = score - previous_score
                time_delta = version_date - datetime.fromisoformat(versions[-2]['timestamp'])
                
                edge = {
                    "from_version_id": previous_version_id,
                    "to_version_id": version_id,
                    "change_type": change_type,
                    "score_delta": score_delta,
                    "time_delta": str(time_delta)
                }
                edges.append(edge)
            
            # Update for next iteration
            previous_version_id = version_id
            previous_text = version_text
            previous_score = score
    
    return versions, edges


def generate_multiple_trends(
    prompt_id: str,
    days: int = 30
) -> Dict[str, Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]]:
    """
    Generate synthetic histories with all three trend types.
    
    Args:
        prompt_id: UUID of the prompt
        days: Number of days of history
        
    Returns:
        Dict with keys "improving", "degrading", "oscillating", values are (versions, edges) tuples
    """
    results = {}
    
    for trend_type in ["improving", "degrading", "oscillating"]:
        # Temporarily override random choice
        original_choice = random.choice
        random.choice = lambda x: trend_type if trend_type in x else original_choice(x)
        
        versions, edges = generate_synthetic_history(prompt_id, days)
        results[trend_type] = (versions, edges)
        
        # Restore random choice
        random.choice = original_choice
    
    return results


def _compute_change_type(old_text: str, new_text: str) -> str:
    """
    Compute change type using difflib edit distance.
    
    Args:
        old_text: Previous version text
        new_text: New version text
        
    Returns:
        str: "structure", "wording", "length", or "other"
    """
    ratio = difflib.SequenceMatcher(None, old_text, new_text).ratio()
    
    if ratio < 0.5:
        return "structure"
    
    length_ratio = len(new_text) / max(len(old_text), 1)
    if length_ratio > 1.5 or length_ratio < 0.5:
        return "length"
    
    return "wording"


def _compute_change_magnitude(old_text: str, new_text: str) -> float:
    """
    Compute change magnitude (normalized edit distance).
    
    Args:
        old_text: Previous version text
        new_text: New version text
        
    Returns:
        float: 0-1 (0 = identical, 1 = completely different)
    """
    ratio = difflib.SequenceMatcher(None, old_text, new_text).ratio()
    return 1.0 - ratio


def main():
    """Example usage of temporal data generator."""
    print("📊 Temporal Data Generator Demo")
    print("=" * 50)
    
    # Generate synthetic history
    prompt_id = str(uuid.uuid4())
    print(f"\\nGenerating 30-day history for prompt: {prompt_id}")
    
    versions, edges = generate_synthetic_history(prompt_id, days=30, versions_per_day=2)
    
    print(f"\\n✅ Generated {len(versions)} versions and {len(edges)} edges")
    print(f"\\nFirst 3 versions:")
    for i, version in enumerate(versions[:3]):
        print(f"  {i+1}. Score: {version['score']:.1f} | Type: {version['change_type']} | Time: {version['timestamp'][:10]}")
    
    print(f"\\nLast 3 versions:")
    for i, version in enumerate(versions[-3:]):
        print(f"  {len(versions)-2+i}. Score: {version['score']:.1f} | Type: {version['change_type']} | Time: {version['timestamp'][:10]}")
    
    print(f"\\nCausal edges summary:")
    print(f"  Total edges: {len(edges)}")
    change_type_counts = {}
    for edge in edges:
        ct = edge['change_type']
        change_type_counts[ct] = change_type_counts.get(ct, 0) + 1
    
    for ct, count in change_type_counts.items():
        print(f"  {ct}: {count} edges")
    
    print(f"\\n💡 Usage:")
    print("  from temporal_data_generator import generate_synthetic_history")
    print("  versions, edges = generate_synthetic_history(prompt_id, days=30)")
    print("  storage.save_prompt_version_chain(prompt_id, versions)")
    print("  storage.save_causal_edges(prompt_id, edges)")


if __name__ == "__main__":
    main()


