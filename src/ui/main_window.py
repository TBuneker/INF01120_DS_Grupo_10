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
        self.title("Reprodutor Musical")
        self.geometry("900x540")
        self.minsize(780, 500)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self._texto_entrada = TextoEntrada()
        self._interpretador = InterpretadorFuga()
        self._exportador = ExportadorMIDI()
        self._reprodutor = ReprodutorMusical()
        self._composicao_atual: ComposicaoMusical | None = None
        self._midi_temporario = Path(gettempdir()) / "gerador_fuga_texto.mid"

        self._criar_layout()

    def _criar_layout(self) -> None:
        self.configure(fg_color="#f4f4f4")
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Reprodutor Musical",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#000000",
        )
        titulo.grid(row=0, column=0, columnspan=2, pady=(8, 10), sticky="ew")

        area_texto = ctk.CTkFrame(
            self,
            fg_color="#b8b8b8",
            border_width=2,
            border_color="#000000",
            corner_radius=0,
        )
        area_texto.grid(row=1, column=0, padx=(22, 18), pady=(0, 8), sticky="nsew")
        area_texto.grid_columnconfigure(0, weight=1)
        area_texto.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            area_texto,
            text="Insira o texto:",
            font=ctk.CTkFont(size=16),
            text_color="#111111",
            anchor="w",
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="ew")

        self._texto = ctk.CTkTextbox(
            area_texto,
            wrap="word",
            font=("Consolas", 15),
            fg_color="#b8b8b8",
            text_color="#000000",
            border_width=0,
            corner_radius=0,
        )
        self._texto.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self._texto.insert(
            "1.0",
            "[0] C D E F\n[4] G A H C\n[8] E F G A",
        )

        botoes_texto = ctk.CTkFrame(self, fg_color="transparent")
        botoes_texto.grid(row=2, column=0, padx=(22, 18), pady=(0, 18), sticky="ew")
        botoes_texto.grid_columnconfigure(1, weight=1)
        self._criar_botao(
            botoes_texto, "Carregar arquivo(.txt)", self._carregar_texto, 0, width=150
        )
        self._criar_botao(botoes_texto, "Salvar", self._salvar_texto, 2, width=96)

        painel_config = ctk.CTkFrame(
            self,
            fg_color="#b8b8b8",
            border_width=2,
            border_color="#000000",
            corner_radius=0,
        )
        painel_config.grid(row=1, column=1, padx=(14, 22), pady=(0, 8), sticky="new")
        painel_config.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            painel_config,
            text="Configuracoes Iniciais",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000",
        ).grid(row=0, column=0, padx=14, pady=(12, 4), sticky="ew")

        self._bpm_entry = self._criar_campo_config(painel_config, "BPM:", "120", 1)
        self._instrumento_entry = self._criar_campo_config(
            painel_config, "Instrumento:", "6", 2
        )
        self._volume_entry = self._criar_campo_config(
            painel_config, "Volume:", "100", 3
        )
        self._oitava_entry = self._criar_campo_config(
            painel_config, "Oitava padrao:", "6", 4
        )

        self._criar_botao(
            painel_config,
            "Salvar",
            self._salvar_configuracoes,
            0,
            width=110,
            linha=5,
            pady=(10, 14),
        )

        acoes = ctk.CTkFrame(self, fg_color="transparent")
        acoes.grid(row=3, column=0, columnspan=2, padx=22, pady=(10, 4), sticky="ew")
        for coluna in range(6):
            acoes.grid_columnconfigure(coluna, weight=1)

        self._criar_botao(acoes, "Gerar musica", self._gerar_musica, 0, width=140)
        self._criar_botao(acoes, "Salvar MIDI", self._salvar_midi, 1, width=140)
        self._criar_botao(acoes, "Reproduzir", self._reproduzir, 2, width=140)
        self._criar_botao(acoes, "Pausar", self._pausar, 3, width=120)
        self._criar_botao(acoes, "Retomar", self._retomar, 4, width=120)
        self._criar_botao(acoes, "Parar", self._parar, 5, width=120)

        self._status = ctk.CTkLabel(
            self,
            text="Pronto.",
            anchor="w",
            font=ctk.CTkFont(size=13),
            text_color="#111111",
        )
        self._status.grid(row=4, column=0, columnspan=2, padx=22, pady=(0, 12), sticky="ew")

    def _criar_campo_config(
        self, pai: ctk.CTkFrame, rotulo: str, valor_inicial: str, linha: int
    ) -> ctk.CTkEntry:
        bloco = ctk.CTkFrame(pai, fg_color="transparent")
        bloco.grid(row=linha, column=0, padx=18, pady=4, sticky="ew")
        bloco.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            bloco,
            text=rotulo,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#111111",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        campo = ctk.CTkEntry(
            bloco,
            width=98,
            height=30,
            fg_color="#eeeeee",
            text_color="#000000",
            border_color="#000000",
            corner_radius=0,
        )
        campo.insert(0, valor_inicial)
        campo.grid(row=0, column=1, padx=(10, 0), sticky="e")
        return campo

    def _criar_botao(
        self,
        pai: ctk.CTkFrame,
        texto: str,
        comando,
        coluna: int,
        width: int,
        linha: int = 0,
        pady: int | tuple[int, int] = 6,
    ) -> None:
        ctk.CTkButton(
            pai,
            text=texto,
            command=comando,
            width=width,
            height=36,
            fg_color="#b8b8b8",
            hover_color="#a5a5a5",
            border_width=2,
            border_color="#000000",
            text_color="#000000",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=0,
        ).grid(row=linha, column=coluna, padx=6, pady=pady)

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

    def _salvar_configuracoes(self) -> None:
        try:
            self._ler_configuracoes()
            self._definir_status("Configuracoes iniciais salvas.")
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
        config_global, config_voz = self._ler_configuracoes()
        return self._interpretador.interpretar(
            texto=self._obter_texto(),
            configuracao_global=config_global,
            configuracao_primeira_voz=config_voz,
        )

    def _ler_configuracoes(self) -> tuple[ConfiguracaoGlobal, ConfiguracaoVoz]:
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
        config_global.validar()
        config_voz.validar()
        return config_global, config_voz

    def _obter_texto(self) -> str:
        return self._texto.get("1.0", "end-1c")

    def _definir_status(self, mensagem: str) -> None:
        self._status.configure(text=mensagem)

    def _mostrar_erro(self, erro: Exception) -> None:
        mensagem = str(erro)
        self._definir_status(f"Erro: {mensagem}")
        messagebox.showerror("Erro", mensagem)
