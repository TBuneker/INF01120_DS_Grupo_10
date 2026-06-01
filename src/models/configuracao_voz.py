from dataclasses import dataclass

from src.models.instrumento_general_midi import InstrumentoGeneralMIDI


@dataclass
class ConfiguracaoVoz:
    instrumento: int
    volume: int
    oitava: int

    def validar(self) -> None:
        InstrumentoGeneralMIDI.validar_numero(self.instrumento)
        if not 0 <= self.volume <= 127:
            raise ValueError("Volume deve estar entre 0 e 127.")
        if not 0 <= self.oitava <= 9:
            raise ValueError("Oitava deve estar entre 0 e 9.")
