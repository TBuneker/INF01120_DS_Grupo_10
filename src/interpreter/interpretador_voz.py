import re

from src.interpreter.contexto_interpretacao import ContextoInterpretacao
from src.interpreter.gerenciador_regras import GerenciadorRegras
from src.interpreter.regras_padrao import criar_regras_padrao
from src.models.configuracao_global import ConfiguracaoGlobal
from src.models.configuracao_voz import ConfiguracaoVoz
from src.models.sequencia_musical import SequenciaMusical
from src.models.voz_musical import VozMusical


PADRAO_ATRASO = re.compile(r"^\s*\[(\d+)\]\s*")


class InterpretadorVoz:
    def __init__(self, gerenciador_regras: GerenciadorRegras | None = None) -> None:
        self._gerenciador_regras = gerenciador_regras or GerenciadorRegras(
            criar_regras_padrao()
        )

    def interpretar(
        self,
        linha: str,
        indice_voz: int,
        configuracao_global: ConfiguracaoGlobal,
        configuracao_voz: ConfiguracaoVoz,
    ) -> VozMusical:
        atraso, conteudo = self._extrair_atraso(linha)
        sequencia = SequenciaMusical()
        contexto = ContextoInterpretacao(
            configuracao_global=configuracao_global,
            configuracao_voz=configuracao_voz,
            beat_atual=float(atraso),
            bpm_atual=configuracao_global.bpm_inicial,
        )

        posicao = 0
        while posicao < len(conteudo):
            eventos, consumidos = self._gerenciador_regras.aplicar(
                conteudo, posicao, contexto
            )
            for evento in eventos:
                sequencia.adicionar(evento)
            posicao += consumidos

        return VozMusical(
            indice=indice_voz,
            configuracao_inicial=configuracao_voz,
            sequencia=sequencia,
            atraso_beats=atraso,
        )

    def _extrair_atraso(self, linha: str) -> tuple[int, str]:
        resultado = PADRAO_ATRASO.match(linha)
        if resultado is None:
            return 0, linha
        return int(resultado.group(1)), linha[resultado.end() :]
