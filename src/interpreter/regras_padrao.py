from src.interpreter.contexto_interpretacao import ContextoInterpretacao
from src.interpreter.regra_mapeamento import RegraMapeamento
from src.models.evento_musical import EventoMusical
from src.models.instrumento_general_midi import InstrumentoGeneralMIDI


NOTAS_BASE: dict[str, int] = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
    "H": 10,
}


def nota_para_midi(nome: str, oitava: int) -> int:
    if nome == "Mb":
        semitom = 3
    else:
        semitom = NOTAS_BASE[nome]
    return (oitava + 1) * 12 + semitom


def _emitir_nota(contexto: ContextoInterpretacao, nota_midi: int) -> EventoMusical:
    InstrumentoGeneralMIDI.validar_numero(contexto.configuracao_voz.instrumento)
    evento = EventoMusical.nota(
        nota_midi=nota_midi,
        volume=contexto.configuracao_voz.volume,
        instrumento=contexto.configuracao_voz.instrumento,
    )
    contexto.ultima_nota_midi = nota_midi
    contexto.ultimo_caractere_foi_nota = True
    contexto.registrar_avanco(evento.duracao_beats)
    return evento


def _emitir_pausa(contexto: ContextoInterpretacao) -> EventoMusical:
    evento = EventoMusical.pausa()
    contexto.ultimo_caractere_foi_nota = False
    contexto.registrar_avanco(evento.duracao_beats)
    return evento


class RegraMiBemol(RegraMapeamento):
    def aceita(self, texto: str, posicao: int, contexto: ContextoInterpretacao) -> bool:
        return texto[posicao : posicao + 2] == "Mb"

    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        nota = nota_para_midi("Mb", contexto.configuracao_voz.oitava)
        return [_emitir_nota(contexto, nota)], 2


class RegraNotaMaiuscula(RegraMapeamento):
    def aceita(self, texto: str, posicao: int, contexto: ContextoInterpretacao) -> bool:
        caractere = texto[posicao]
        return caractere in NOTAS_BASE and caractere != "V"

    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        nota = nota_para_midi(texto[posicao], contexto.configuracao_voz.oitava)
        return [_emitir_nota(contexto, nota)], 1


class RegraPausaMinuscula(RegraMapeamento):
    def aceita(self, texto: str, posicao: int, contexto: ContextoInterpretacao) -> bool:
        return texto[posicao] in "abcdefgh"

    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        return [_emitir_pausa(contexto)], 1


class RegraEspacoVolume(RegraMapeamento):
    def aceita(self, texto: str, posicao: int, contexto: ContextoInterpretacao) -> bool:
        return texto[posicao] == " "

    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        novo_volume = contexto.limitar_volume(contexto.configuracao_voz.volume * 2)
        contexto.configuracao_voz.volume = novo_volume
        contexto.ultimo_caractere_foi_nota = False
        return [], 1


class RegraInstrumentoFixo(RegraMapeamento):
    def __init__(self, caracteres: set[str], instrumento: int) -> None:
        self._caracteres = caracteres
        self._instrumento = instrumento

    def aceita(self, texto: str, posicao: int, contexto: ContextoInterpretacao) -> bool:
        return texto[posicao] in self._caracteres

    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        contexto.configuracao_voz.instrumento = InstrumentoGeneralMIDI.validar_numero(
            self._instrumento
        )
        contexto.ultimo_caractere_foi_nota = False
        return [EventoMusical.instrumento(self._instrumento)], 1


class RegraDigitoPar(RegraMapeamento):
    def aceita(self, texto: str, posicao: int, contexto: ContextoInterpretacao) -> bool:
        caractere = texto[posicao]
        return caractere.isdigit() and int(caractere) % 2 == 0

    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        novo_instrumento = min(127, contexto.configuracao_voz.instrumento + int(texto[posicao]))
        contexto.configuracao_voz.instrumento = novo_instrumento
        contexto.ultimo_caractere_foi_nota = False
        return [EventoMusical.instrumento(novo_instrumento)], 1


class RegraOitava(RegraMapeamento):
    def aceita(self, texto: str, posicao: int, contexto: ContextoInterpretacao) -> bool:
        return texto[posicao] in {"?", ".", "V"}

    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        if texto[posicao] == "V":
            contexto.configuracao_voz.oitava = contexto.limitar_oitava(
                contexto.configuracao_voz.oitava - 1
            )
        else:
            proxima = contexto.configuracao_voz.oitava + 1
            if proxima > contexto.configuracao_global.oitava_maxima:
                proxima = contexto.configuracao_voz.oitava
            contexto.configuracao_voz.oitava = contexto.limitar_oitava(proxima)
        contexto.ultimo_caractere_foi_nota = False
        return [], 1


class RegraBpm(RegraMapeamento):
    def aceita(self, texto: str, posicao: int, contexto: ContextoInterpretacao) -> bool:
        return texto[posicao] in {">", "<"}

    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        delta = 10 if texto[posicao] == ">" else -10
        contexto.bpm_atual = max(
            contexto.configuracao_global.bpm_minimo,
            min(contexto.configuracao_global.bpm_maximo, contexto.bpm_atual + delta),
        )
        contexto.ultimo_caractere_foi_nota = False
        return [EventoMusical.tempo(contexto.bpm_atual, contexto.beat_atual)], 1


class RegraRepeticaoOuPausa(RegraMapeamento):
    def aceita(self, texto: str, posicao: int, contexto: ContextoInterpretacao) -> bool:
        return True

    def aplicar(
        self, texto: str, posicao: int, contexto: ContextoInterpretacao
    ) -> tuple[list[EventoMusical], int]:
        if contexto.ultimo_caractere_foi_nota and contexto.ultima_nota_midi is not None:
            return [_emitir_nota(contexto, contexto.ultima_nota_midi)], 1
        return [_emitir_pausa(contexto)], 1


def criar_regras_padrao() -> list[RegraMapeamento]:
    return [
        RegraMiBemol(),
        RegraNotaMaiuscula(),
        RegraPausaMinuscula(),
        RegraEspacoVolume(),
        RegraInstrumentoFixo({"!"}, 22),
        RegraInstrumentoFixo({"O", "o", "I", "i", "U", "u"}, 109),
        RegraDigitoPar(),
        RegraOitava(),
        RegraInstrumentoFixo({";"}, 14),
        RegraInstrumentoFixo({","}, 19),
        RegraInstrumentoFixo({"1", "3", "5", "7", "9"}, 14),
        RegraBpm(),
        RegraRepeticaoOuPausa(),
    ]