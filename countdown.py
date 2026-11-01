"""Estado da contagem, independente dos eventos e das janelas Qt."""

from collections.abc import Callable
from time import monotonic


class Countdown:
    """Calcula o tempo restante com um relógio monotónico substituível em testes."""

    def __init__(self, seconds: int, clock: Callable[[], float] = monotonic):
        """Carrega uma duração em segundos e começa no estado parado."""
        self._clock = clock
        self.loaded_seconds = 0
        self._elapsed_seconds = 0.0
        self._started_at: float | None = None
        self.load(seconds)

    @property
    def remaining_seconds(self) -> int:
        """Devolve a duração menos os segundos completos efetivamente decorridos."""
        elapsed = self._elapsed_seconds
        if self._started_at is not None:
            elapsed += self._clock() - self._started_at
        return self.loaded_seconds - int(elapsed)

    @property
    def is_running(self) -> bool:
        """Indica se a contagem está a decorrer."""
        return self._started_at is not None

    def load(self, seconds: int) -> None:
        """Para a contagem e carrega uma duração não negativa."""
        if seconds < 0:
            raise ValueError("A duração não pode ser negativa.")
        self.loaded_seconds = seconds
        self.reset()

    def start(self) -> None:
        """Retoma a contagem ou recarrega uma duração positiva já esgotada."""
        if self.remaining_seconds <= 0 < self.loaded_seconds:
            self.reset()
        if self._started_at is None:
            self._started_at = self._clock()

    def pause(self) -> None:
        """Para e conserva também a fração de segundo decorrida."""
        if self._started_at is not None:
            self._elapsed_seconds += self._clock() - self._started_at
            self._started_at = None

    def reset(self) -> None:
        """Para e repõe a duração carregada."""
        self._elapsed_seconds = 0.0
        self._started_at = None
