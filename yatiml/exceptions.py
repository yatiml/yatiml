from typing import Any


class RecognitionError(RuntimeError):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
