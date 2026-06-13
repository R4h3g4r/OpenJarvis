import pyaudio
import wave
import os

from openjarvis.tools._stubs import BaseTool, ToolSpec
from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from faster_whisper import WhisperModel

@ToolRegistry.register("ear")
class EarTool(BaseTool):
    def __init__(self):
        self.model = WhisperModel("small", device="cpu", compute_type="int8")
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="ear",
            description="Escucha audio del micrófono durante N segundos y lo transcribe.",
            parameters={
                "type": "object",
                "properties": {
                    "duration": {"type": "integer", "description": "Segundos a grabar"}
                }
            }
        )

    def execute(self, duration: int = 5, **params) -> ToolResult:
        filename = "temp_input.wav"
        p = pyaudio.PyAudio()
        
        stream = p.open(format=self.format, channels=self.channels,
                        rate=self.rate, input=True,
                        frames_per_buffer=self.chunk)
        
        frames = []
        for i in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        segments, info = self.model.transcribe(filename, beam_size=5)
        text = " ".join([segment.text for segment in segments])
        
        if os.path.exists(filename):
            os.remove(filename)

        return ToolResult(content=text if text else "No se detectó voz.")