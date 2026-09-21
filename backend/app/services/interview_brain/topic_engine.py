from typing import Dict, Any, List, Optional

class TechnicalTopicEngine:
    """
    Selects technical topics and coding problem domains dynamically based on:
    - Job Description requirements
    - Candidate Resume skills
    - Role & Seniority
    - Previously answered questions
    - Remaining interview time
    """

    TOPIC_CATALOG = {
        "Python": ["Data Structures", "Algorithms", "Dictionaries / Hash Maps", "Generators / Decorators", "AsyncIO", "OOP / Design Patterns"],
        "JavaScript": ["Arrays & Objects", "Async / Await / Promises", "Closure & Scope", "DOM / Virtual DOM", "Performance Optimization"],
        "Java": ["Collections Framework", "Streams API", "Multithreading & Concurrency", "JVM Memory Management", "Design Patterns"],
        "Go": ["Goroutines & Channels", "Slices & Maps", "Interfaces & Structs", "Concurrency Patterns"],
        "Algorithms": ["Arrays & Strings", "Two Pointers / Sliding Window", "Hash Tables", "Trees & Graphs", "Dynamic Programming"]
    }

    def select_topic(
        self,
        job_description: str,
        resume_text: str,
        role: str,
        seniority: str = "Mid-Level",
        previous_topics: Optional[List[str]] = None,
        remaining_time_minutes: int = 30
    ) -> Dict[str, Any]:
        previous_topics = previous_topics or []
        jd_lower = (job_description or "").lower()
        resume_lower = (resume_text or "").lower()
        role_lower = (role or "").lower()

        primary_language = "Python"
        if "javascript" in role_lower or "react" in jd_lower or "frontend" in role_lower:
            primary_language = "JavaScript"
        elif "java" in role_lower or "spring" in jd_lower:
            primary_language = "Java"
        elif "golang" in role_lower or "go developer" in role_lower:
            primary_language = "Go"

        if remaining_time_minutes < 5:
            return {
                "primary_language": primary_language,
                "topic": "Wrap-Up & Complexity Review",
                "subtopics": ["Complexity Analysis", "Optimization", "System Tradeoffs"],
                "should_start_coding": False,
                "reason": "Less than 5 minutes remaining. Transition to code review & technical wrap-up."
            }

        available_subtopics = self.TOPIC_CATALOG.get(primary_language, self.TOPIC_CATALOG["Algorithms"])
        unused_subtopics = [t for t in available_subtopics if t not in previous_topics]
        selected_subtopic = unused_subtopics[0] if unused_subtopics else available_subtopics[0]

        return {
            "primary_language": primary_language,
            "topic": primary_language,
            "subtopics": [selected_subtopic],
            "should_start_coding": True,
            "seniority_level": seniority,
            "reason": f"Selected {selected_subtopic} in {primary_language} matching role '{role}' and candidate background."
        }
