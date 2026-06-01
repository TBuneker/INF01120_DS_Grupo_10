from abc import ABC, abstractmethod

from src.interpreter.contexto_interpretacao import ContextoInterpretacao
from src.models.evento_musical import EventoMusical


class RegraMapeamento(ABC):
    @abstractmethod
    def aceita(self, texto: str, posicao: int, contexto: ContextoInterpretacao) -> bool:
        raise NotImplementedError

    @abstractmethod
    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        """Retorna os eventos gerados e quantos caracteres foram consumidos."""
        raise NotImplementedError