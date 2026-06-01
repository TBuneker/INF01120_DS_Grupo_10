from dataclasses import dataclass, field

from src.models.configuracao_global import ConfiguracaoGlobal
from src.models.evento_musical import EventoMusical, TipoEvento
from src.models.voz_musical import VozMusical


@dataclass
class ComposicaoMusical:
    configuracao_global: ConfiguracaoGlobal
    vozes: list[VozMusical] = field(default_factory=list)
    eventos_tempo: list[EventoMusical] = field(default_factory=list)

    def adicionar_voz(self, voz: VozMusical) -> None:
        self.vozes.append(voz)
        self.eventos_tempo.extend(
            evento for evento in voz.sequencia.eventos if evento.tipo == TipoEvento.TEMPO
        )
        self.eventos_tempo.sort(key=lambda evento: evento.beat_absoluto or 0)

    @property
    def duracao_beats(self) -> float:
        if not self.vozes:
            return 0.0
        return max(voz.duracao_total_beats for voz in self.vozes)
