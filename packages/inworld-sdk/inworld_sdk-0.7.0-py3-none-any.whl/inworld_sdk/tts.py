import copy
from dataclasses import dataclass
import json
from typing import Any, AsyncGenerator, cast, List, Optional, Union

from .http_wrapper import HTTPWrapper
from .models import AudioConfig
from .models import SynthesizeSpeechRequest
from .models import SynthesizeSpeechResponse
from .models import TTSAudioEncoding
from .models import TTSLanguageCodes
from .models import TTSModelIds
from .models import TTSVoiceIds
from .models import VoiceResponse


@dataclass
class _TTSOptions:
    voiceId: TTSVoiceIds
    modelId: TTSModelIds
    audioConfig: AudioConfig
    temperature: Optional[float]


class TTS:
    """TTS API client"""

    def __init__(
        self,
        client: HTTPWrapper,
    ):
        """Constructor for TTS class"""
        self.__client = client
        self.__opts: _TTSOptions = _TTSOptions(
            voiceId="Olivia",
            modelId="inworld-tts-1",
            audioConfig={
                "audioEncoding": None,
                "bitRate": None,
                "sampleRateHertz": None,
                "pitch": None,
                "speakingRate": None,
            },
            temperature=None,
        )

    def update_options(
        self,
        voiceId: Optional[TTSVoiceIds] = None,
        modelId: Optional[TTSModelIds] = None,
        temperature: Optional[float] = None,
        audioEncoding: Optional[TTSAudioEncoding] = None,
        bitRate: Optional[int] = None,
        sampleRateHertz: Optional[int] = None,
        pitch: Optional[float] = None,
        speakingRate: Optional[float] = None,
    ) -> None:
        if modelId is not None:
            self.__opts.modelId = modelId
        if voiceId is not None:
            self.__opts.voiceId = voiceId
        if temperature is not None:
            self.__opts.temperature = temperature
        if audioEncoding is not None:
            self.__opts.audioConfig["audioEncoding"] = audioEncoding
        if bitRate is not None:
            self.__opts.audioConfig["bitRate"] = bitRate
        if sampleRateHertz is not None:
            self.__opts.audioConfig["sampleRateHertz"] = sampleRateHertz
        if pitch is not None:
            self.__opts.audioConfig["pitch"] = pitch
        if speakingRate is not None:
            self.__opts.audioConfig["speakingRate"] = speakingRate

    async def synthesizeSpeech(
        self,
        text: str,
        voiceId: Optional[TTSVoiceIds] = None,
        modelId: Optional[TTSModelIds] = None,
        temperature: Optional[float] = None,
        audioEncoding: Optional[TTSAudioEncoding] = None,
        bitRate: Optional[int] = None,
        sampleRateHertz: Optional[int] = None,
        pitch: Optional[float] = None,
        speakingRate: Optional[float] = None,
    ) -> SynthesizeSpeechResponse:
        """Synthesize speech"""
        data = self._generate_request(
            text,
            voiceId,
            modelId,
            temperature,
            audioEncoding,
            bitRate,
            sampleRateHertz,
            pitch,
            speakingRate,
        )
        response = await self.__client.request(
            "post",
            "/tts/v1/voice",
            data=data,
        )
        return cast(SynthesizeSpeechResponse, response)

    async def synthesizeSpeechStream(
        self,
        text: str,
        voiceId: Optional[TTSVoiceIds] = None,
        modelId: Optional[TTSModelIds] = None,
        temperature: Optional[float] = None,
        audioEncoding: Optional[TTSAudioEncoding] = None,
        bitRate: Optional[int] = None,
        sampleRateHertz: Optional[int] = None,
        pitch: Optional[float] = None,
        speakingRate: Optional[float] = None,
    ) -> AsyncGenerator[SynthesizeSpeechResponse, None]:
        """Synthesize speech as a stream"""
        data = self._generate_request(
            text,
            voiceId,
            modelId,
            temperature,
            audioEncoding,
            bitRate,
            sampleRateHertz,
            pitch,
            speakingRate,
        )

        async with self.__client.stream(
            "post",
            "/tts/v1/voice:stream",
            data,
        ) as response:
            async for chunk in response.aiter_lines():
                if chunk:
                    chunk_data = json.loads(chunk)
                    if isinstance(chunk_data, dict) and chunk_data.get("result"):
                        yield cast(SynthesizeSpeechResponse, chunk_data["result"])

    async def voices(
        self,
        languageCode: Optional[Union[TTSLanguageCodes, str]] = None,
        modelId: Optional[Union[TTSModelIds, str]] = None,
    ) -> List[VoiceResponse]:
        """Get voices"""
        data: dict[str, Any] = {}
        if languageCode:
            data["languageCode"] = languageCode
        if modelId:
            data["modelId"] = modelId

        response = await self.__client.request("get", "/tts/v1/voices", data=data)
        voices = response.get("voices", [])
        return cast(List[VoiceResponse], voices)

    def _generate_request(
        self,
        text: str,
        voiceId: Optional[TTSVoiceIds] = None,
        modelId: Optional[TTSModelIds] = None,
        temperature: Optional[float] = None,
        audioEncoding: Optional[TTSAudioEncoding] = None,
        bitRate: Optional[int] = None,
        sampleRateHertz: Optional[int] = None,
        pitch: Optional[float] = None,
        speakingRate: Optional[float] = None,
    ) -> SynthesizeSpeechRequest:
        audioConfig = copy.copy(self.__opts.audioConfig)
        if audioEncoding is not None:
            audioConfig["audioEncoding"] = audioEncoding
        if bitRate is not None:
            audioConfig["bitRate"] = bitRate
        if sampleRateHertz is not None:
            audioConfig["sampleRateHertz"] = sampleRateHertz
        if pitch is not None:
            audioConfig["pitch"] = pitch
        if speakingRate is not None:
            audioConfig["speakingRate"] = speakingRate

        return {
            "text": text,
            "voiceId": voiceId or self.__opts.voiceId,
            "modelId": modelId or self.__opts.modelId,
            "audioConfig": audioConfig,
            "temperature": temperature or self.__opts.temperature,
        }
