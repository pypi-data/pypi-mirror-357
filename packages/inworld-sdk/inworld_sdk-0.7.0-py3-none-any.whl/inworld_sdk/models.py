from typing import Literal, Optional, TypedDict

__all__ = [
    "AudioConfig",
    "SynthesizeSpeechResponse",
    "SynthesizeSpeechUsage",
    "TTSAudioEncoding",
    "TTSLanguageCodes",
    "TTSModelIds",
    "TTSVoiceIds",
    "VoiceResponse",
]

TTSAudioEncoding = Literal["LINEAR16", "MP3", "OGG_OPUS", "ALAW", "MULAW"]

TTSLanguageCodes = Literal["en"]

TTSModelIds = Literal["inworld-tts-1"]

TTSVoiceIds = Literal[
    "Alex",
    "Amit",
    "Ashley",
    "Craig",
    "Deborah",
    "Dennis",
    "Dominus",
    "Edward",
    "Eileen",
    "Elizabeth",
    "Esmeralda",
    "Hades",
    "Julia",
    "Mark",
    "Olivia",
    "Pixie",
    "Priya",
    "Ralph",
    "Ronald",
    "Sarah",
    "Shaun",
    "Theodore",
    "Timmy",
    "Timothy",
    "Wendy",
]


class AudioConfig(TypedDict):
    audioEncoding: Optional[TTSAudioEncoding]
    bitRate: Optional[int]
    sampleRateHertz: Optional[int]
    pitch: Optional[float]
    speakingRate: Optional[float]


class VoiceResponse(TypedDict):
    languages: list[TTSLanguageCodes]
    voiceId: TTSVoiceIds
    displayName: str
    description: str


class SynthesizeSpeechUsage(TypedDict):
    processedCharactersCount: int
    modelId: TTSModelIds


class SynthesizeSpeechResponse(TypedDict):
    audioContent: str
    usage: SynthesizeSpeechUsage


class SynthesizeSpeechRequest(TypedDict):
    text: str
    voiceId: TTSVoiceIds
    modelId: TTSModelIds
    audioConfig: Optional[AudioConfig]
    temperature: Optional[float]
