from dataclasses import dataclass
from enum import Enum


class TipoEvento(str, Enum):
    NOTA = "nota"
    PAUSA = "pausa"
    INSTRUMENTO = "instrumento"
    TEMPO = "tempo"
    VOLUME = "volume"
    OITAVA = "oitava"


@dataclass(frozen=True)
class EventoMusical:
    tipo: TipoEvento
    duracao_beats: float = 0.0
    nota_midi: int | None = None
    volume: int | None = None
    instrumento: int | None = None
    bpm: int | None = None
    beat_absoluto: float | None = None
    descricao: str = ""

    @classmethod
    def nota(cls, nota_midi: int, volume: int, instrumento: int) -> "EventoMusical":
        return cls(
            tipo=TipoEvento.NOTA,
            duracao_beats=1.0,
            nota_midi=nota_midi,
            volume=volume,
            instrumento=instrumento,
            descricao="nota",
        )

    @classmethod
    def pausa(cls) -> "EventoMusical":
        return cls(tipo=TipoEvento.PAUSA, duracao_beats=1.0, descricao="pausa")

    @classmethod
    def instrumento(cls, instrumento: int) -> "EventoMusical":
        return cls(
            tipo=TipoEvento.INSTRUMENTO,
            instrumento=instrumento,
            descricao="mudanca de instrumento",
        )

    @classmethod
    def tempo(cls, bpm: int, beat_absoluto: float) -> "EventoMusical":
        return cls(
            tipo=TipoEvento.TEMPO,
            bpm=bpm,
            beat_absoluto=beat_absoluto,
            descricao="mudanca de BPM",
        )
