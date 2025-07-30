import inspect
import sys
from pathlib import Path
from typing import Optional

from .base import SpeechToSpeechHarness, SpeechToSpeechHarnessMeta
from .models.gemini import GeminiSpeechToSpeechHarness
from .models.nova import NovaSpeechToSpeechHarness
from .models.openai import OpenAISpeechToSpeechHarness


def spoken(
        model_name: str,
        input_f: Path,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None, # TODO: use the default for the model
    ) -> SpeechToSpeechHarness:
    cls = SpeechToSpeechHarnessMeta.name_to_harness(model_name)
    model = cls.Model(model_name)

    kwargs = dict(system_prompt=system_prompt)
    if temperature is not None:
        # fallback to base class default if not passed
        kwargs["temperature"] = temperature

    return cls.from_file(
        model,
        input_f,
        **kwargs
    )

sys.modules[__name__] = spoken
