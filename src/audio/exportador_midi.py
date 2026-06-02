from pathlib import Path

from src.models.composicao_musical import ComposicaoMusical
from src.models.evento_musical import TipoEvento


class ExportadorMIDI:
    def __init__(self, ticks_por_beat: int = 480) -> None:
        self._ticks_por_beat = ticks_por_beat

    def salvar(self, composicao: ComposicaoMusical, caminho: str | Path) -> Path:
        try:
            from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo
        except ImportError as erro:
            raise RuntimeError("A biblioteca mido nao esta instalada.") from erro

        destino = Path(caminho)
        if destino.suffix.lower() not in {"", ".mid", ".midi"}:
            raise ValueError("O arquivo MIDI deve ter extensao .mid ou .midi.")
        if destino.suffix == "":
            destino = destino.with_suffix(".mid")

        midi = MidiFile(ticks_per_beat=self._ticks_por_beat)
        midi.tracks.append(self._criar_trilha_tempo(composicao, MetaMessage, bpm2tempo))

        for voz in composicao.vozes:
            trilha = MidiTrack()
            trilha.append(MetaMessage("track_name", name=f"Voz {voz.indice}", time=0))
            canal = voz.indice % 16
            instrumento_atual = voz.configuracao_inicial.instrumento
            trilha.append(
                Message("program_change", program=instrumento_atual, channel=canal, time=0)
            )
            pendente_ticks = int(voz.atraso_beats * self._ticks_por_beat)

            for evento in voz.sequencia.eventos:
                if evento.tipo == TipoEvento.PAUSA:
                    pendente_ticks += int(evento.duracao_beats * self._ticks_por_beat)
                elif evento.tipo == TipoEvento.INSTRUMENTO and evento.instrumento is not None:
                    instrumento_atual = evento.instrumento
                    trilha.append(
                        Message(
                            "program_change",
                            program=instrumento_atual,
                            channel=canal,
                            time=pendente_ticks,
                        )
                    )
                    pendente_ticks = 0
                elif evento.tipo == TipoEvento.NOTA and evento.nota_midi is not None:
                    if evento.instrumento is not None and evento.instrumento != instrumento_atual:
                        instrumento_atual = evento.instrumento
                        trilha.append(
                            Message(
                                "program_change",
                                program=instrumento_atual,
                                channel=canal,
                                time=pendente_ticks,
                            )
                        )
                        pendente_ticks = 0
                    trilha.append(
                        Message(
                            "note_on",
                            note=evento.nota_midi,
                            velocity=evento.volume or 0,
                            channel=canal,
                            time=pendente_ticks,
                        )
                    )
                    trilha.append(
                        Message(
                            "note_off",
                            note=evento.nota_midi,
                            velocity=0,
                            channel=canal,
                            time=int(evento.duracao_beats * self._ticks_por_beat),
                        )
                    )
                    pendente_ticks = 0

            trilha.append(MetaMessage("end_of_track", time=pendente_ticks))
            midi.tracks.append(trilha)

        midi.save(destino)
        return destino

    def _criar_trilha_tempo(self, composicao: ComposicaoMusical, MetaMessage, bpm2tempo):
        from mido import MidiTrack

        trilha = MidiTrack()
        trilha.append(MetaMessage("track_name", name="Tempo", time=0))
        trilha.append(
            MetaMessage(
                "set_tempo",
                tempo=bpm2tempo(composicao.configuracao_global.bpm_inicial),
                time=0,
            )
        )

        ultimo_tick = 0
        for evento in sorted(composicao.eventos_tempo, key=lambda item: item.beat_absoluto or 0):
            if evento.bpm is None or evento.beat_absoluto is None:
                continue
            tick = int(evento.beat_absoluto * self._ticks_por_beat)
            trilha.append(
                MetaMessage(
                    "set_tempo",
                    tempo=bpm2tempo(evento.bpm),
                    time=max(0, tick - ultimo_tick),
                )
            )
            ultimo_tick = tick

        trilha.append(MetaMessage("end_of_track", time=0))
        return trilha
