import logging
from typing import Dict, Any

logger = logging.getLogger("followup_engine")

class FollowUpEngine:
    """
    Decides the next state machine action based on candidate answer analysis:
    - FOLLOW_UP
    - CLARIFY
    - NEXT_TOPIC
    - INCREASE_DIFFICULTY
    - DECREASE_DIFFICULTY
    - MOVE_TO_NEXT_STAGE
    """

    @staticmethod
    def decide_next_action(
        current_stage: str,
        current_difficulty: str,
        analysis: Dict[str, Any],
        questions_asked_in_stage: int = 1,
        max_stage_questions: int = 4
    ) -> Dict[str, Any]:

        depth = analysis.get("technical_depth", 0.7)
        relevance = analysis.get("relevance", 0.8)
        completeness = analysis.get("completeness", 0.7)

        # Stage boundary check
        if questions_asked_in_stage >= max_stage_questions:
            return {
                "action": "MOVE_TO_NEXT_STAGE",
                "reason": f"Target question count ({max_stage_questions}) reached for stage {current_stage}.",
                "difficulty": current_difficulty
            }

        # Quality evaluation
        if relevance < 0.5:
            return {
                "action": "CLARIFY",
                "reason": "Answer lacked sufficient relevance to the asked question.",
                "difficulty": current_difficulty
            }

        if depth < 0.4:
            new_diff = "EASY" if current_difficulty == "MEDIUM" else "MEDIUM"
            return {
                "action": "DECREASE_DIFFICULTY",
                "reason": "Answer technical depth was basic. Adjusting difficulty target.",
                "difficulty": new_diff
            }

        if depth >= 0.85 and completeness >= 0.8:
            new_diff = "HARD" if current_difficulty == "MEDIUM" else current_difficulty
            return {
                "action": "INCREASE_DIFFICULTY",
                "reason": "Strong answer demonstrating deep mastery. Escalating difficulty target.",
                "difficulty": new_diff
            }

        if completeness < 0.7:
            return {
                "action": "FOLLOW_UP",
                "reason": "Answer was relevant but incomplete on key details.",
                "difficulty": current_difficulty
            }

        return {
            "action": "NEXT_TOPIC",
            "reason": "Satisfactory answer provided. Moving to next technical topic.",
            "difficulty": current_difficulty
        }
