from typing import Dict, Any, List

class DifficultyEngine:
    """
    Manages adaptive interview difficulty based on candidate performance.
    Levels: EASY -> MEDIUM -> HARD -> EXPERT
    """

    DIFFICULTY_LEVELS = ["EASY", "MEDIUM", "HARD", "EXPERT"]

    def adapt_difficulty(
        self,
        current_difficulty: str,
        recent_scores: List[float],
        seniority: str = "Mid-Level"
    ) -> Dict[str, Any]:
        curr = (current_difficulty or "MEDIUM").upper()
        if curr not in self.DIFFICULTY_LEVELS:
            curr = "MEDIUM"

        idx = self.DIFFICULTY_LEVELS.index(curr)
        if not recent_scores:
            return {
                "previous_difficulty": curr,
                "new_difficulty": curr,
                "reason": "No recent answers yet, maintaining initial difficulty level."
            }

        avg_score = sum(recent_scores) / len(recent_scores)
        new_idx = idx

        if avg_score >= 0.85 and idx < len(self.DIFFICULTY_LEVELS) - 1:
            new_idx += 1
            reason = f"High performance score ({avg_score:.2f} >= 0.85). Increasing difficulty."
        elif avg_score < 0.50 and idx > 0:
            new_idx -= 1
            reason = f"Candidate struggling ({avg_score:.2f} < 0.50). Decreasing difficulty."
        else:
            reason = f"Performance score ({avg_score:.2f}) within nominal range. Maintaining difficulty."

        new_diff = self.DIFFICULTY_LEVELS[new_idx]
        return {
            "previous_difficulty": curr,
            "new_difficulty": new_diff,
            "avg_score": round(avg_score, 2),
            "reason": reason
        }
