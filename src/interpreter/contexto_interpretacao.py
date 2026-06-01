from dataclasses import dataclass

from src.models.configuracao_global import ConfiguracaoGlobal
from src.models.configuracao_voz import ConfiguracaoVoz


@dataclass
class ContextoInterpretacao:
    configuracao_global: ConfiguracaoGlobal
    configuracao_voz: ConfiguracaoVoz
    beat_atual: float
    bpm_atual: int
    ultima_nota_midi: int | None = None
    ultimo_caractere_foi_nota: bool = False

    def limitar_volume(self, volume: int) -> int:
        return max(0, min(self.configuracao_global.volume_maximo, volume))

    def limitar_oitava(self, oitava: int) -> int:
        return max(
            self.configuracao_global.oitava_minima,
            min(self.configuracao_global.oitava_maxima, oitava),
        )

    def registrar_avanco(self, duracao_beats: float) -> None:
        self.beat_atual += duracao_beats
