import re
import logging
from typing import Dict, Any, Optional

from integrations.meeting.base import MeetingProvider
from integrations.meeting.google_meet import GoogleMeetProvider
from integrations.meeting.zoom import ZoomProvider
from integrations.meeting.teams import TeamsProvider

logger = logging.getLogger("meeting_provider_factory")


class MeetingProviderFactory:
    """
    Factory for instantiating MeetingProvider implementations based on explicit provider type
    or meeting URL pattern analysis (Google Meet, Zoom, Microsoft Teams).
    """

    _providers: Dict[str, MeetingProvider] = {}

    @classmethod
    def get_provider(cls, provider_type: Optional[str] = None, meeting_url: Optional[str] = None) -> MeetingProvider:
        """
        Returns MeetingProvider instance. If provider_type is omitted, inspects meeting_url.
        """
        selected = (provider_type or "").upper()

        if not selected and meeting_url:
            if "meet.google.com" in meeting_url.lower():
                selected = "GOOGLE_MEET"
            elif "zoom.us" in meeting_url.lower():
                selected = "ZOOM"
            elif "teams.microsoft.com" in meeting_url.lower() or "teams.live.com" in meeting_url.lower():
                selected = "TEAMS"

        if selected not in cls._providers:
            if selected == "ZOOM":
                cls._providers["ZOOM"] = ZoomProvider()
            elif selected == "TEAMS":
                cls._providers["TEAMS"] = TeamsProvider()
            else:
                # Default to GoogleMeetProvider
                cls._providers["GOOGLE_MEET"] = GoogleMeetProvider()
                selected = "GOOGLE_MEET"

        return cls._providers[selected]
