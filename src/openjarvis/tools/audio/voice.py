from openjarvis.tools._stubs import BaseTool, ToolSpec
from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from kokoro_onnx import Kokoro

@ToolRegistry.register("voice")
class VoiceTool(BaseTool):
    def __init__(self):
        self.engine = Kokoro("kokoro-v0_19.onnx", "voices.json")

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="voice",
            description="Convierte texto a voz (TTS) para hablar con el usuario."
        )

    def execute(self, text: str, **params) -> ToolResult:
        return ToolResult(content=f"Jarvis ha hablado: {text}")