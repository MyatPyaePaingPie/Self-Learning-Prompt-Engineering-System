# analytics for token + score data

def compute_analytics(history):
    if not history:
        return {}

    total_in = sum(h.input_tokens for h in history)
    total_out = sum(h.output_tokens for h in history)
    avg_score = sum(h.total_score for h in history) / len(history)

    top_prompt = max(history, key=lambda h: h.total_score)

    return {
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "average_score": round(avg_score, 2),
        "highest_scoring_prompt": {
            "id": top_prompt.id,
            "prompt": top_prompt.original_prompt,
            "score": top_prompt.total_score
        }
    }
