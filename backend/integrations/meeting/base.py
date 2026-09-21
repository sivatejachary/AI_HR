from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class MeetingCapabilities(BaseModel):
    """Explicit provider capability model."""
    audioReceive: bool = True
    audioSend: bool = True
    videoReceive: bool = True
    videoSend: bool = False
    screenShareReceive: bool = True
    participantEvents: bool = True
    activeSpeaker: bool = True
    transcript: bool = True
    media_api_available: bool = True
    provider_name: str = "GENERIC"
    note: Optional[str] = None


class MeetingProvider(ABC):
    """
    Abstract Base Class for video meeting platform providers (Google Meet, Zoom, Teams).
    Encapsulates platform-specific REST API and Media API calls.
    """

    @abstractmethod
    def validate_meeting(self, meeting: Dict[str, Any]) -> bool:
        """Validates meeting URL and access permissions."""
        pass

    @abstractmethod
    def prepare_meeting(self, meeting: Dict[str, Any]) -> Dict[str, Any]:
        """Prepares conference session metadata and participant credentials."""
        pass

    @abstractmethod
    def join(self, meeting: Dict[str, Any]) -> Dict[str, Any]:
        """Connects AI interviewer bot to the meeting."""
        pass

    @abstractmethod
    def leave(self, meeting: Dict[str, Any]) -> Dict[str, Any]:
        """Safely disconnects AI interviewer bot from the meeting."""
        pass

    @abstractmethod
    def get_meeting_state(self, meeting: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves active meeting status, duration, and connection state."""
        pass

    @abstractmethod
    def get_participants(self, meeting: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Returns active meeting participants with identities and roles."""
        pass

    @abstractmethod
    def get_capabilities(self) -> MeetingCapabilities:
        """Returns explicit capability matrix for this provider."""
        pass

    @abstractmethod
    def send_audio(self, meeting: Dict[str, Any], audio_chunk: bytes) -> bool:
        """Transmits ElevenLabs spoken audio into the meeting room."""
        pass

    @abstractmethod
    def receive_audio(self, meeting: Dict[str, Any]) -> Optional[bytes]:
        """Receives incoming candidate audio stream."""
        pass

    @abstractmethod
    def receive_video(self, meeting: Dict[str, Any]) -> Optional[bytes]:
        """Receives incoming candidate video stream if enabled."""
        pass

    @abstractmethod
    def receive_screen_share(self, meeting: Dict[str, Any]) -> Optional[bytes]:
        """Receives screen share media stream if present."""
        pass

    @abstractmethod
    def mute(self, meeting: Dict[str, Any]) -> bool:
        """Mutes AI bot audio."""
        pass

    @abstractmethod
    def unmute(self, meeting: Dict[str, Any]) -> bool:
        """Unmutes AI bot audio."""
        pass

    @abstractmethod
    def get_active_speaker(self, meeting: Dict[str, Any]) -> Optional[str]:
        """Returns participant ID of current active speaker."""
        pass

    @abstractmethod
    def handle_participant_joined(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handles participant joined event."""
        pass

    @abstractmethod
    def handle_participant_left(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handles participant left event."""
        pass

    @abstractmethod
    def handle_meeting_ended(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handles meeting end event."""
        pass

    @abstractmethod
    def disconnect(self, meeting: Dict[str, Any]) -> bool:
        """Emergency disconnect of meeting session."""
        pass
