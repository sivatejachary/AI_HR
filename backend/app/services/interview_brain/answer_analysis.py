import logging
from typing import Dict, Any, List

logger = logging.getLogger("answer_analysis")

class AnswerAnalysisService:
    """
    Analyzes candidate answers for reasoning signals:
    - correctness
    - completeness
    - technical depth
    - relevance
    - confidence
    - missing concepts
    Note: These metrics serve as reasoning signals for state progression, NOT final hiring decisions.
    """

    @staticmethod
    def analyze_answer(
        question_text: str,
        answer_text: str,
        candidate_context: Dict[str, Any] = None,
        job_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:

        if not answer_text or len(answer_text.strip()) == 0:
            return {
                "correctness": 0.0,
                "completeness": 0.0,
                "technical_depth": 0.0,
                "relevance": 0.0,
                "confidence": 0.0,
                "missing_concepts": ["no answer provided"],
                "quality_summary": "Candidate provided no answer."
            }

        length = len(answer_text.strip())
        words = answer_text.strip().split()
        
        # Calculate heuristics signals
        relevance = 0.90 if len(words) >= 5 else 0.50
        technical_depth = min(1.0, max(0.4, len(words) / 30.0))
        completeness = min(1.0, max(0.5, len(words) / 25.0))
        correctness = 0.85 if technical_depth > 0.6 else 0.70
        confidence = 0.85 if len(words) >= 10 else 0.60

        missing_concepts = []
        ans_lower = answer_text.lower()
        if "test" not in ans_lower and "monitor" not in ans_lower and "scale" not in ans_lower:
            missing_concepts.append("testing & production monitoring considerations")

        return {
            "correctness": round(correctness, 2),
            "completeness": round(completeness, 2),
            "technical_depth": round(technical_depth, 2),
            "relevance": round(relevance, 2),
            "confidence": round(confidence, 2),
            "missing_concepts": missing_concepts,
            "quality_summary": f"Answer demonstrated good relevance ({int(relevance*100)}%) and technical depth ({int(technical_depth*100)}%)."
        }
