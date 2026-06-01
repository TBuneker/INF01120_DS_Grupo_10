from dataclasses import dataclass, field

from src.models.evento_musical import EventoMusical


@dataclass
class SequenciaMusical:
    eventos: list[EventoMusical] = field(default_factory=list)

    def adicionar(self, evento: EventoMusical) -> None:
        self.eventos.append(evento)

    @property
    def duracao_beats(self) -> float:
        return sum(evento.duracao_beats for evento in self.eventos)
