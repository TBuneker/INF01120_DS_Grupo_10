from dataclasses import dataclass


@dataclass
class ConfiguracaoGlobal:
    bpm_inicial: int = 120
    bpm_minimo: int = 30
    bpm_maximo: int = 240
    volume_maximo: int = 127
    oitava_minima: int = 0
    oitava_maxima: int = 9

    def validar(self) -> None:
        if not self.bpm_minimo <= self.bpm_inicial <= self.bpm_maximo:
            raise ValueError(
                f"BPM inicial deve estar entre {self.bpm_minimo} e {self.bpm_maximo}."
            )
