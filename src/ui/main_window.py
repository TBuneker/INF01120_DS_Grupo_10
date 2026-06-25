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
from src.interpreter.interpretador_fuga import (
    INSTRUMENTOS_PADRAO,
    OITAVAS_PADRAO,
    VOLUMES_PADRAO,
)


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Reprodutor Musical")
        self.geometry("1120x720")
        self.minsize(980, 640)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self._texto_entrada = TextoEntrada()
        self._interpretador = InterpretadorFuga()
        self._exportador = ExportadorMIDI()
        self._reprodutor = ReprodutorMusical()
        self._composicao_atual: ComposicaoMusical | None = None
        self._midi_temporario = Path(gettempdir()) / "gerador_fuga_texto.mid"
        self._reproducao_pausada = False
        self._controles_vozes: list[dict[str, ctk.CTkBaseClass]] = []
        self._quantidade_vozes_exibidas = 0

        self._criar_layout()

    def _criar_layout(self) -> None:
        self.configure(fg_color="#f4f4f4")
        self.grid_columnconfigure(0, weight=8, minsize=720)
        self.grid_columnconfigure(1, weight=0, minsize=330)
        self.grid_rowconfigure(1, weight=1, minsize=250)

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
        area_texto.grid(row=1, column=0, padx=(22, 10), pady=(0, 8), sticky="nsew")
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
            height=390,
        )
        self._texto.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self._texto.bind("<KeyRelease>", self._ao_texto_alterado)

        botoes_texto = ctk.CTkFrame(self, fg_color="transparent")
        botoes_texto.grid(row=3, column=0, columnspan=2, padx=25, pady=(10, 4), sticky="ew")
        for coluna in range(7):
            botoes_texto.grid_columnconfigure(coluna, weight=1)
        self._criar_botao(
            botoes_texto, "Carregar .txt", self._carregar_texto, 0, width=140
        )
        self._criar_botao(botoes_texto, "Salvar .txt", self._salvar_texto, 1, width=140)
        

        painel_config = ctk.CTkFrame(
            self,
            width=360,
            fg_color="#b8b8b8",
            border_width=2,
            border_color="#000000",
            corner_radius=0,
        )
        painel_config.grid(row=2, column=0, padx=22, pady=(0, 8), sticky="w")
        painel_config.grid_propagate(False)
        painel_config.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            painel_config,
            text="Configurações Iniciais",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000",
        ).grid(row=0, column=0, padx=14, pady=(12, 4), sticky="ew")

        self._bpm_entry = self._criar_campo_config(painel_config, "BPM:", "120", 1)
        self._volume_entry = self._criar_campo_config(
            painel_config, "Volume:", "100", 2
        )
        self._oitava_entry = self._criar_campo_config(
            painel_config, "Oitava padrão:", "6", 3
        )

        self._criar_painel_vozes()

        acoes = ctk.CTkFrame(self, fg_color="transparent")
        acoes.grid(row=4, column=0, columnspan=2, padx=22, pady=(10, 4), sticky="ew")
        for coluna in range(4):
            acoes.grid_columnconfigure(coluna, weight=1)

        self._criar_botao(acoes, "Gerar musica", self._gerar_musica, 0, width=140)
        self._criar_botao(acoes, "Salvar MIDI", self._salvar_midi, 1, width=140)
        self._criar_botao(acoes, "Reproduzir", self._reproduzir, 2, width=140)
        self._pausar_retomar_button = self._criar_botao(
            acoes, "Pausar", self._alternar_pausa_retomada, 3, width=140
        )

        self._status = ctk.CTkLabel(
            self,
            text="Pronto.",
            anchor="w",
            font=ctk.CTkFont(size=13),
            text_color="#111111",
        )
        self._status.grid(row=5, column=0, columnspan=2, padx=22, pady=(0, 12), sticky="ew")
        self._atualizar_painel_vozes()

    def _criar_campo_config(
        self, pai: ctk.CTkFrame, rotulo: str, valor_inicial: str, linha: int
    ) -> ctk.CTkEntry:
        bloco = ctk.CTkFrame(pai, fg_color="transparent")
        bloco.grid(row=linha, column=0, padx=18, pady=4)
        ctk.CTkLabel(
            bloco,
            text=rotulo,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#111111",
            anchor="e",
            width=150,
        ).grid(row=0, column=0, sticky="e")
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
        campo.grid(row=0, column=1, padx=(10, 0), sticky="w")
        return campo

    def _criar_painel_vozes(self) -> None:
        painel_vozes = ctk.CTkFrame(
            self,
            fg_color="#b8b8b8",
            border_width=2,
            border_color="#000000",
            corner_radius=0,
        )
        painel_vozes.grid(
            row=1,
            column=1,
            rowspan=2,
            padx=(0, 22),
            pady=(0, 8),
            sticky="nsew",
        )
        painel_vozes.grid_columnconfigure(0, weight=1)
        painel_vozes.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            painel_vozes,
            text="Vozes",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000",
        ).grid(row=0, column=0, padx=14, pady=(12, 8), sticky="ew")

        self._vozes_frame = ctk.CTkScrollableFrame(
            painel_vozes,
            fg_color="#b8b8b8",
            scrollbar_button_color="#999999",
            scrollbar_button_hover_color="#888888",
        )
        self._vozes_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self._vozes_frame.grid_columnconfigure(0, weight=1)

    def _ao_texto_alterado(self, _evento=None) -> None:
        self._invalidar_composicao()
        self._atualizar_painel_vozes()

    def _invalidar_composicao(self, _valor=None) -> None:
        self._composicao_atual = None

    def _contar_vozes_no_texto(self) -> int:
        linhas = self._obter_texto().splitlines()
        linhas_com_conteudo = [linha for linha in linhas if linha != ""]
        return len(linhas_com_conteudo) or 1

    def _atualizar_painel_vozes(self) -> None:
        quantidade_vozes = self._contar_vozes_no_texto()
        if quantidade_vozes == self._quantidade_vozes_exibidas:
            return

        configuracoes_atuais = self._obter_configuracoes_vozes()
        for filho in self._vozes_frame.winfo_children():
            filho.destroy()

        self._controles_vozes = []
        self._quantidade_vozes_exibidas = quantidade_vozes
        for indice in range(quantidade_vozes):
            instrumento, oitava = self._obter_padrao_voz(indice, configuracoes_atuais)
            self._criar_linha_voz(indice, instrumento, oitava)

    def _criar_linha_voz(self, indice: int, instrumento: int, oitava: int) -> None:
        linha = ctk.CTkFrame(
            self._vozes_frame,
            fg_color="#b8b8b8",
            border_width=1,
            border_color="#000000",
            corner_radius=0,
        )
        linha.grid(row=indice, column=0, padx=0, pady=(0, 8), sticky="ew")
        linha.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            linha,
            text=f"Voz {indice + 1}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#000000",
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(8, 4), sticky="ew")

        ctk.CTkLabel(
            linha,
            text="Instrumento:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#111111",
            anchor="w",
        ).grid(row=1, column=0, padx=10, pady=(2, 8), sticky="w")

        instrumento_entry = ctk.CTkEntry(
            linha,
            width=76,
            height=30,
            fg_color="#eeeeee",
            text_color="#000000",
            border_color="#000000",
            corner_radius=0,
        )
        instrumento_entry.insert(0, str(instrumento))
        instrumento_entry.bind("<KeyRelease>", self._invalidar_composicao)
        instrumento_entry.grid(row=1, column=1, padx=10, pady=(2, 8), sticky="e")

        ctk.CTkLabel(
            linha,
            text="Oitava:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#111111",
            anchor="w",
        ).grid(row=2, column=0, padx=10, pady=(0, 8), sticky="w")

        oitava_entry = ctk.CTkEntry(
            linha,
            width=76,
            height=30,
            fg_color="#eeeeee",
            text_color="#000000",
            border_color="#000000",
            corner_radius=0,
        )
        oitava_entry.insert(0, str(oitava))
        oitava_entry.bind("<KeyRelease>", self._invalidar_composicao)
        oitava_entry.grid(row=2, column=1, padx=10, pady=(0, 8), sticky="e")

        self._controles_vozes.append(
            {
                "instrumento": instrumento_entry,
                "oitava": oitava_entry,
            }
        )

    def _obter_padrao_voz(
        self, indice: int, configuracoes_atuais: list[tuple[int, int]]
    ) -> tuple[int, int]:
        if indice < len(configuracoes_atuais):
            return configuracoes_atuais[indice]

        posicao = indice % len(OITAVAS_PADRAO)
        if indice == 0:
            try:
                oitava_primeira_voz = int(self._oitava_entry.get())
            except ValueError:
                oitava_primeira_voz = OITAVAS_PADRAO[posicao]
            return INSTRUMENTOS_PADRAO[posicao], oitava_primeira_voz
        return INSTRUMENTOS_PADRAO[posicao], OITAVAS_PADRAO[posicao]

    def _obter_configuracoes_vozes(self) -> list[tuple[int, int]]:
        configuracoes = []
        for controle in self._controles_vozes:
            instrumento = int(controle["instrumento"].get())
            oitava = int(controle["oitava"].get())
            configuracoes.append((instrumento, oitava))
        return configuracoes

    def _criar_botao(
        self,
        pai: ctk.CTkFrame,
        texto: str,
        comando,
        coluna: int,
        width: int,
        linha: int = 0,
        pady: int | tuple[int, int] = 6,
    ) -> ctk.CTkButton:
        botao = ctk.CTkButton(
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
        )
        botao.grid(row=linha, column=coluna, padx=6, pady=pady)
        return botao

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
            self._ao_texto_alterado()
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
            self._reproducao_pausada = False
            self._pausar_retomar_button.configure(text="Pausar")
            self._definir_status("Reproducao iniciada.")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _alternar_pausa_retomada(self) -> None:
        if self._reproducao_pausada:
            self._retomar()
        else:
            self._pausar()

    def _pausar(self) -> None:
        try:
            self._reprodutor.pausar()
            self._reproducao_pausada = True
            self._pausar_retomar_button.configure(text="Retomar")
            self._definir_status("Reproducao pausada.")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _retomar(self) -> None:
        try:
            self._reprodutor.retomar()
            self._reproducao_pausada = False
            self._pausar_retomar_button.configure(text="Pausar")
            self._definir_status("Reproducao retomada.")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _criar_composicao(self) -> ComposicaoMusical:
        config_global, configuracoes_vozes = self._ler_configuracoes()
        return self._interpretador.interpretar(
            texto=self._obter_texto(),
            configuracao_global=config_global,
            configuracoes_vozes=configuracoes_vozes,
        )

    def _ler_configuracoes(self) -> tuple[ConfiguracaoGlobal, list[ConfiguracaoVoz]]:
        bpm = int(self._bpm_entry.get())
        volume = int(self._volume_entry.get())
        config_global = ConfiguracaoGlobal(bpm_inicial=bpm)
        config_global.validar()

        configuracoes_vozes = []
        for indice, (instrumento, oitava) in enumerate(self._obter_configuracoes_vozes()):
            posicao = indice % len(VOLUMES_PADRAO)
            volume_voz = volume if indice == 0 else VOLUMES_PADRAO[posicao]
            config_voz = ConfiguracaoVoz(
                instrumento=instrumento,
                volume=volume_voz,
                oitava=oitava,
            )
            config_voz.validar()
            configuracoes_vozes.append(config_voz)

        return config_global, configuracoes_vozes

    def _obter_texto(self) -> str:
        return self._texto.get("1.0", "end-1c")

    def _definir_status(self, mensagem: str) -> None:
        self._status.configure(text=mensagem)

    def _mostrar_erro(self, erro: Exception) -> None:
        mensagem = str(erro)
        self._definir_status(f"Erro: {mensagem}")
        messagebox.showerror("Erro", mensagem)
