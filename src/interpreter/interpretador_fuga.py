from src.interpreter.interpretador_voz import InterpretadorVoz
from src.models.composicao_musical import ComposicaoMusical
from src.models.configuracao_global import ConfiguracaoGlobal
from src.models.configuracao_voz import ConfiguracaoVoz


OITAVAS_PADRAO = (6, 5, 4, 3)
VOLUMES_PADRAO = (100, 80, 60, 40)
INSTRUMENTOS_PADRAO = (6, 19, 0, 70)


class InterpretadorFuga:
    def __init__(self, interpretador_voz: InterpretadorVoz | None = None) -> None:
        self._interpretador_voz = interpretador_voz or InterpretadorVoz()

    def interpretar(
        self,
        texto: str,
        configuracao_global: ConfiguracaoGlobal | None = None,
        configuracao_primeira_voz: ConfiguracaoVoz | None = None,
        configuracoes_vozes: list[ConfiguracaoVoz] | None = None,
    ) -> ComposicaoMusical:
        config_global = configuracao_global or ConfiguracaoGlobal()
        config_global.validar()
        composicao = ComposicaoMusical(configuracao_global=config_global)

        linhas = texto.splitlines() or [""]
        for linha in linhas:
            if linha == "" and len(linhas) > 1:
                continue
            indice = len(composicao.vozes)
            config_voz = self._criar_configuracao_voz(
                indice, configuracao_primeira_voz, configuracoes_vozes
            )
            voz = self._interpretador_voz.interpretar(
                linha=linha,
                indice_voz=indice,
                configuracao_global=config_global,
                configuracao_voz=config_voz,
            )
            composicao.adicionar_voz(voz)

        return composicao

    def _criar_configuracao_voz(
        self,
        indice: int,
        configuracao_primeira_voz: ConfiguracaoVoz | None,
        configuracoes_vozes: list[ConfiguracaoVoz] | None = None,
    ) -> ConfiguracaoVoz:
        if configuracoes_vozes is not None and indice < len(configuracoes_vozes):
            configuracao_voz = configuracoes_vozes[indice]
            configuracao_voz.validar()
            return ConfiguracaoVoz(
                instrumento=configuracao_voz.instrumento,
                volume=configuracao_voz.volume,
                oitava=configuracao_voz.oitava,
            )
        if indice == 0 and configuracao_primeira_voz is not None:
            configuracao_primeira_voz.validar()
            return ConfiguracaoVoz(
                instrumento=configuracao_primeira_voz.instrumento,
                volume=configuracao_primeira_voz.volume,
                oitava=configuracao_primeira_voz.oitava,
            )
        posicao = indice % len(OITAVAS_PADRAO)
        configuracao = ConfiguracaoVoz(
            instrumento=INSTRUMENTOS_PADRAO[posicao],
            volume=VOLUMES_PADRAO[posicao],
            oitava=OITAVAS_PADRAO[posicao],
        )
        configuracao.validar()
        return configuracao
