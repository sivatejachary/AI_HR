import os
import uuid
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("online_compiler")

class OnlineCodingProvider:
    """
    Provider abstraction for approved external online compilers / coding platforms.
    Responsibility: Provide coding problem URL, candidate session URL, supported languages,
    session status, and optional official submission result integration.
    Does NOT execute candidate code locally or on our infrastructure.
    """

    def __init__(self, platform_name: Optional[str] = None, base_url: Optional[str] = None):
        self.platform_name = platform_name or os.getenv("CODING_PLATFORM_NAME", "Compiler Explorer")
        self.base_url = (base_url or os.getenv("CODING_PLATFORM_BASE_URL", "https://godbolt.org")).rstrip("/")

    def get_supported_languages(self) -> List[str]:
        return ["python", "javascript", "typescript", "java", "cpp", "go", "rust", "sql"]

    def generate_coding_url(self, problem_id: str, language: str = "python", session_id: Optional[str] = None) -> str:
        """
        Generates a direct candidate session URL for the approved external platform.
        """
        lang = language.lower()
        if "godbolt" in self.base_url:
            lang_map = {
                "python": "python",
                "javascript": "js",
                "typescript": "ts",
                "java": "java",
                "cpp": "c_cpp",
                "go": "go",
                "rust": "rust"
            }
            mapped_lang = lang_map.get(lang, "python")
            return f"{self.base_url}/#g:!((g:!((h:code,i:1,l:{mapped_lang}))))"
        
        # Generic vendor-neutral platform URL format with problem & session query params
        sess_token = session_id or str(uuid.uuid4())[:8]
        return f"{self.base_url}/session/{sess_token}?problem={problem_id}&lang={lang}"

    def create_candidate_session(self, problem_id: str, candidate_id: str, language: str = "python") -> Dict[str, Any]:
        """
        Creates metadata for candidate coding session on approved platform.
        """
        session_token = str(uuid.uuid4())
        coding_url = self.generate_coding_url(problem_id=problem_id, language=language, session_id=session_token)
        
        return {
            "session_token": session_token,
            "coding_platform": self.platform_name,
            "base_url": self.base_url,
            "coding_url": coding_url,
            "language": language,
            "problem_id": problem_id,
            "status": "WAITING_FOR_SCREEN_SHARE",
            "has_official_api": False
        }

    def fetch_official_submission_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Optional official integration hook if the vendor provides a webhook or official API.
        Returns None if no vendor API is configured (AI relies solely on visible screen stream).
        """
        return None
