from pathlib import Path
from tempfile import gettempdir
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.audio.exportador_midi import ExportadorMIDI
from src.audio.reprodutor_musical import ReprodutorMusical
from src.interpreter.interpretador_fuga import InterpretadorFuga
from src.models.composicao_musical import ComposicaoMusical
from src.models.configuracao_global import ConfiguracaoGlobal
from src.models.configuracao_voz import ConfiguracaoVoz
from src.models.texto_entrada import TextoEntrada


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Gerador de Fuga por Texto")
        self.geometry("980x680")
        self.minsize(860, 560)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self._texto_entrada = TextoEntrada()
        self._interpretador = InterpretadorFuga()
        self._exportador = ExportadorMIDI()
        self._reprodutor = ReprodutorMusical()
        self._composicao_atual: ComposicaoMusical | None = None
        self._midi_temporario = Path(gettempdir()) / "gerador_fuga_texto.mid"

        self._criar_layout()

    def _criar_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        barra = ctk.CTkFrame(self, corner_radius=0)
        barra.grid(row=0, column=0, sticky="ew")
        barra.grid_columnconfigure(8, weight=1)

        self._bpm_entry = self._criar_campo(barra, "BPM", "120", 0)
        self._volume_entry = self._criar_campo(barra, "Volume V0", "100", 1)
        self._instrumento_entry = self._criar_campo(barra, "Instrumento V0", "6", 2)
        self._oitava_entry = self._criar_campo(barra, "Oitava V0", "6", 3)

        ctk.CTkButton(barra, text="Carregar .txt", command=self._carregar_texto).grid(
            row=0, column=4, padx=6, pady=10
        )
        ctk.CTkButton(barra, text="Salvar .txt", command=self._salvar_texto).grid(
            row=0, column=5, padx=6, pady=10
        )
        ctk.CTkButton(barra, text="Gerar musica", command=self._gerar_musica).grid(
            row=0, column=6, padx=6, pady=10
        )
        ctk.CTkButton(barra, text="Salvar MIDI", command=self._salvar_midi).grid(
            row=0, column=7, padx=6, pady=10
        )

        self._texto = ctk.CTkTextbox(self, wrap="word", font=("Consolas", 15))
        self._texto.grid(row=1, column=0, padx=14, pady=(14, 8), sticky="nsew")
        self._texto.insert(
            "1.0",
            "[0] C D E F\n[4] G A H C\n[8] E F G A",
        )

        rodape = ctk.CTkFrame(self, corner_radius=0)
        rodape.grid(row=2, column=0, sticky="ew")
        rodape.grid_columnconfigure(4, weight=1)

        ctk.CTkButton(rodape, text="Reproduzir", command=self._reproduzir).grid(
            row=0, column=0, padx=8, pady=10
        )
        ctk.CTkButton(rodape, text="Pausar", command=self._pausar).grid(
            row=0, column=1, padx=8, pady=10
        )
        ctk.CTkButton(rodape, text="Retomar", command=self._retomar).grid(
            row=0, column=2, padx=8, pady=10
        )
        ctk.CTkButton(rodape, text="Parar", command=self._parar).grid(
            row=0, column=3, padx=8, pady=10
        )

        self._status = ctk.CTkLabel(rodape, text="Pronto.", anchor="w")
        self._status.grid(row=0, column=4, padx=10, pady=10, sticky="ew")

    def _criar_campo(
        self, pai: ctk.CTkFrame, rotulo: str, valor_inicial: str, coluna: int
    ) -> ctk.CTkEntry:
        bloco = ctk.CTkFrame(pai, fg_color="transparent")
        bloco.grid(row=0, column=coluna, padx=6, pady=6)
        ctk.CTkLabel(bloco, text=rotulo).pack(anchor="w")
        campo = ctk.CTkEntry(bloco, width=92)
        campo.insert(0, valor_inicial)
        campo.pack()
        return campo

    def _carregar_texto(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Carregar texto",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return
        try:
            conteudo = self._texto_entrada.carregar(caminho)
            self._texto.delete("1.0", "end")
            self._texto.insert("1.0", conteudo)
            self._definir_status(f"Texto carregado: {Path(caminho).name}")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _salvar_texto(self) -> None:
        try:
            self._texto_entrada.atualizar_conteudo(self._obter_texto())
            caminho = self._texto_entrada.caminho
            if caminho is None:
                destino = filedialog.asksaveasfilename(
                    title="Salvar texto",
                    defaultextension=".txt",
                    filetypes=[("Arquivos de texto", "*.txt")],
                )
                if not destino:
                    return
                caminho = Path(destino)
            salvo = self._texto_entrada.salvar(caminho)
            self._definir_status(f"Texto salvo: {salvo.name}")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _gerar_musica(self) -> None:
        try:
            self._composicao_atual = self._criar_composicao()
            self._exportador.salvar(self._composicao_atual, self._midi_temporario)
            self._definir_status(
                f"Musica gerada com {len(self._composicao_atual.vozes)} voz(es)."
            )
        except Exception as erro:
            self._mostrar_erro(erro)

    def _salvar_midi(self) -> None:
        try:
            composicao = self._composicao_atual or self._criar_composicao()
            destino = filedialog.asksaveasfilename(
                title="Salvar MIDI",
                defaultextension=".mid",
                filetypes=[("Arquivos MIDI", "*.mid *.midi")],
            )
            if not destino:
                return
            salvo = self._exportador.salvar(composicao, destino)
            self._composicao_atual = composicao
            self._definir_status(f"MIDI salvo: {salvo.name}")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _reproduzir(self) -> None:
        try:
            if self._composicao_atual is None or not self._midi_temporario.exists():
                self._gerar_musica()
            self._reprodutor.reproduzir(self._midi_temporario)
            self._definir_status("Reproducao iniciada.")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _pausar(self) -> None:
        try:
            self._reprodutor.pausar()
            self._definir_status("Reproducao pausada.")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _retomar(self) -> None:
        try:
            self._reprodutor.retomar()
            self._definir_status("Reproducao retomada.")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _parar(self) -> None:
        self._reprodutor.parar()
        self._definir_status("Reproducao parada.")

    def _criar_composicao(self) -> ComposicaoMusical:
        bpm = int(self._bpm_entry.get())
        volume = int(self._volume_entry.get())
        instrumento = int(self._instrumento_entry.get())
        oitava = int(self._oitava_entry.get())
        config_global = ConfiguracaoGlobal(bpm_inicial=bpm)
        config_voz = ConfiguracaoVoz(
            instrumento=instrumento,
            volume=volume,
            oitava=oitava,
        )
        return self._interpretador.interpretar(
            texto=self._obter_texto(),
            configuracao_global=config_global,
            configuracao_primeira_voz=config_voz,
        )

    def _obter_texto(self) -> str:
        return self._texto.get("1.0", "end-1c")

    def _definir_status(self, mensagem: str) -> None:
        self._status.configure(text=mensagem)

    def _mostrar_erro(self, erro: Exception) -> None:
        mensagem = str(erro)
        self._definir_status(f"Erro: {mensagem}")
        messagebox.showerror("Erro", mensagem)
