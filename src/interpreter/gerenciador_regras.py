from src.interpreter.contexto_interpretacao import ContextoInterpretacao
from src.interpreter.regra_mapeamento import RegraMapeamento
from src.models.evento_musical import EventoMusical


class GerenciadorRegras:
    def __init__(self, regras: list[RegraMapeamento]) -> None:
        self._regras = regras

    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        for regra in self._regras:
            if regra.aceita(texto, posicao, contexto):
                return regra.aplicar(texto, posicao, contexto)
        raise RuntimeError("Nenhuma regra de mapeamento foi aplicavel.")