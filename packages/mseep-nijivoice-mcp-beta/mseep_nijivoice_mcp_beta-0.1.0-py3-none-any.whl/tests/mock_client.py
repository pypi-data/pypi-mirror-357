"""Mock implementation of the NijiVoiceClient for testing."""
from typing import List, Optional, Dict, Any
from nijivoice.models import VoiceActor, VoiceGenerationRequest, Balance
from nijivoice.exceptions import NijiVoiceAPIError

class MockNijiVoiceClient:
    """Mock implementation of NijiVoiceClient for testing."""
    
    def __init__(self, api_key: Optional[str] = None, timeout: Optional[float] = 30.0):
        """Mock initialization."""
        self.api_key = api_key
        self.timeout = timeout
        self.should_fail = False
        self.headers = {
            "x-api-key": api_key or "",
            "Accept": "application/json",
        }
        self.voice_actors = [
            VoiceActor(
                id="voice-actor-1",
                name="Test Actor 1",
                description="Test description",
                gender="Male",
                age=25,
            ),
            VoiceActor(
                id="voice-actor-2",
                name="Test Actor 2",
                description="Another test description",
                gender="Female",
                age=30,
            ),
        ]
    
    def set_should_fail(self, should_fail: bool):
        """Set whether API calls should fail."""
        self.should_fail = should_fail
    
    async def get_voice_actors(self) -> List[VoiceActor]:
        """Mock implementation of get_voice_actors."""
        if self.should_fail:
            raise NijiVoiceAPIError("Failed to get voice actors", status_code=500)
        return self.voice_actors
    
    async def generate_voice(self, request: VoiceGenerationRequest) -> Dict[str, Any]:
        """Mock implementation of generate_voice."""
        if self.should_fail:
            raise NijiVoiceAPIError("Failed to generate voice", status_code=500)
        return {
            "encoded_voice": "base64_encoded_mock_audio_data",
            "remaining_credits": 100,
            "format": request.format,
            "actor_id": request.id
        }
    
    async def get_balance(self) -> Balance:
        """Mock implementation of get_balance."""
        if self.should_fail:
            raise NijiVoiceAPIError("Failed to get balance", status_code=500)
        return Balance(balance=100)