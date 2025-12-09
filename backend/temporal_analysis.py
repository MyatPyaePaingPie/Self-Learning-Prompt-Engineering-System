"""
Temporal Analysis Module for Self-Learning Prompt Engineering System
Week 12: Temporal Prompt Learning & Causal Analysis
Author: Paing's Assignment

This module provides temporal analysis functions for detecting trends, 
change-points, and causal hints in prompt evolution history.
"""

from typing import List, Dict, Tuple
from datetime import datetime
import statistics
from scipy import stats
import numpy as np


def detect_trend(scores: List[float], timestamps: List[datetime]) -> str:
    """
    Detect trend in prompt scores over time using linear regression.
    
    Args:
        scores: List of judge scores (0-100)
        timestamps: List of corresponding timestamps
        
    Returns:
        str: "improving", "degrading", or "stable"
    """
    if len(scores) < 2:
        return "stable"
    
    # Convert timestamps to numeric values (seconds since epoch)
    time_numeric = [ts.timestamp() for ts in timestamps]
    
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(time_numeric, scores)
    
    # Classify trend based on slope
    if slope > 0.05:
        return "improving"
    elif slope < -0.05:
        return "degrading"
    else:
        return "stable"


def detect_change_points(scores: List[float], threshold: float = 0.2) -> List[int]:
    """
    Detect change points in score sequence using threshold-based method.
    
    Args:
        scores: List of judge scores (0-100)
        threshold: Minimum score delta to qualify as change point (normalized 0-1)
        
    Returns:
        List[int]: Indices where significant changes occur
    """
    if len(scores) < 2:
        return []
    
    change_points = []
    threshold_scaled = threshold * 100  # Scale threshold to match 0-100 score range
    
    for i in range(1, len(scores)):
        delta = abs(scores[i] - scores[i-1])
        if delta > threshold_scaled:
            change_points.append(i)
    
    return change_points


def compute_statistics(scores: List[float]) -> Dict[str, float]:
    """
    Compute basic statistics for score sequence.
    
    Args:
        scores: List of judge scores (0-100)
        
    Returns:
        Dict with avg, std, min, max, count
    """
    if not scores:
        return {
            "avg": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "count": 0
        }
    
    return {
        "avg": statistics.mean(scores),
        "std": statistics.stdev(scores) if len(scores) > 1 else 0.0,
        "min": min(scores),
        "max": max(scores),
        "count": len(scores)
    }


def compute_causal_hints(edges: List[Tuple[str, float]]) -> List[Dict[str, any]]:
    """
    Compute causal hints by grouping edges by change_type and averaging score deltas.
    
    Args:
        edges: List of tuples (change_type, score_delta)
        
    Returns:
        List of dicts sorted by avg_score_delta DESC:
        [{"change_type": str, "avg_score_delta": float, "occurrence_count": int}, ...]
    """
    if not edges:
        return []
    
    # Group by change_type
    groups: Dict[str, List[float]] = {}
    for change_type, score_delta in edges:
        if change_type not in groups:
            groups[change_type] = []
        groups[change_type].append(score_delta)
    
    # Compute averages
    results = []
    for change_type, deltas in groups.items():
        results.append({
            "change_type": change_type,
            "avg_score_delta": statistics.mean(deltas),
            "occurrence_count": len(deltas)
        })
    
    # Sort by avg_score_delta descending
    results.sort(key=lambda x: x["avg_score_delta"], reverse=True)
    
    return results


def normalize_score_delta(delta: float, max_score: float = 100.0) -> float:
    """
    Normalize score delta to 0-1 range.
    
    Args:
        delta: Raw score delta
        max_score: Maximum possible score (default 100)
        
    Returns:
        float: Normalized delta (0-1)
    """
    return abs(delta) / max_score


def compute_score_velocity(scores: List[float], timestamps: List[datetime]) -> float:
    """
    Compute average rate of score change (velocity) over time.
    
    Args:
        scores: List of judge scores
        timestamps: List of corresponding timestamps
        
    Returns:
        float: Score velocity (points per day)
    """
    if len(scores) < 2:
        return 0.0
    
    # Calculate total score change
    total_change = scores[-1] - scores[0]
    
    # Calculate total time span in days
    time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 86400.0
    
    if time_span == 0:
        return 0.0
    
    return total_change / time_span


