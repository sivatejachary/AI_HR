from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class MeetingProvider(ABC):
    @abstractmethod
    def create_meeting(self, session_id: str, title: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def join_meeting(self, meeting_link: str) -> bool:
        pass

class VoiceProvider(ABC):
    @abstractmethod
    def start_session(self, session_id: str, voice_id: str) -> bool:
        pass

    @abstractmethod
    def send_response(self, text: str) -> bool:
        pass

    @abstractmethod
    def end_session(self) -> bool:
        pass

class CodingProvider(ABC):
    @abstractmethod
    def execute_code(self, code: str, language: str) -> Dict[str, Any]:
        pass

class VisionProvider(ABC):
    @abstractmethod
    def analyze_frame(self, frame_data: bytes) -> Dict[str, Any]:
        pass

class EvaluationProvider(ABC):
    @abstractmethod
    def generate_final_evaluation(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
