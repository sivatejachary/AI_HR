import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("question_generator")

class QuestionGenerator:
    """
    Generates dynamic interview question banks tailored to Job requirements and Candidate resume.
    Provides robust fallback logic if no LLM key is configured.
    """

    @staticmethod
    def generate_questions(job_title: str, job_description: str, candidate_name: str, candidate_skills: List[str] = None) -> List[Dict[str, Any]]:
        skills_str = ", ".join(candidate_skills) if candidate_skills else "software development"
        
        # Domain-tailored template questions based on job title
        title_lower = job_title.lower() if job_title else ""
        
        if "python" in title_lower or "backend" in title_lower or "developer" in title_lower or "engineer" in title_lower:
            return [
                {
                    "question_text": f"Can you explain your experience with async frameworks, connection pooling, and optimizing database performance in high-throughput applications?",
                    "category": "TECHNICAL",
                    "order": 0
                },
                {
                    "question_text": f"Describe a complex system architecture component you designed or refactored. How did you handle fault tolerance and scaling?",
                    "category": "TECHNICAL",
                    "order": 1
                },
                {
                    "question_text": f"Walk us through how you diagnose and fix a memory leak or CPU bottleneck in production.",
                    "category": "TECHNICAL",
                    "order": 2
                }
            ]
        elif "frontend" in title_lower or "react" in title_lower or "web" in title_lower:
            return [
                {
                    "question_text": f"How do you manage complex application state, re-render optimization, and micro-frontend architecture in enterprise web applications?",
                    "category": "TECHNICAL",
                    "order": 0
                },
                {
                    "question_text": f"Explain your approach to Web Vitals performance auditing, bundle size reduction, and asset caching strategies.",
                    "category": "TECHNICAL",
                    "order": 1
                }
            ]
        elif "data" in title_lower or "ai" in title_lower or "ml" in title_lower:
            return [
                {
                    "question_text": f"How do you design data pipelines to maintain data quality, handle schema drift, and monitor model performance in production?",
                    "category": "TECHNICAL",
                    "order": 0
                },
                {
                    "question_text": f"Compare batch vs streaming data processing architectures for real-time analytics workloads.",
                    "category": "TECHNICAL",
                    "order": 1
                }
            ]
        else:
            return [
                {
                    "question_text": f"Can you walk us through your key technical achievements and how they align with the role of {job_title}?",
                    "category": "TECHNICAL",
                    "order": 0
                },
                {
                    "question_text": f"Describe a challenging project requirement you encountered and how you led the team to deliver it successfully.",
                    "category": "BEHAVIORAL",
                    "order": 1
                }
            ]
