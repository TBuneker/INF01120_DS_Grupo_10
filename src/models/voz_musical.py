from dataclasses import dataclass

from src.models.configuracao_voz import ConfiguracaoVoz
from src.models.sequencia_musical import SequenciaMusical


@dataclass
class VozMusical:
    indice: int
    configuracao_inicial: ConfiguracaoVoz
    sequencia: SequenciaMusical
    atraso_beats: int = 0

    @property
    def duracao_total_beats(self) -> float:
        return self.atraso_beats + self.sequencia.duracao_beats
