from dataclasses import dataclass
from pathlib import Path


@dataclass
class TextoEntrada:
    conteudo: str = ""
    caminho: Path | None = None
    modificado: bool = False

    def carregar(self, caminho: str | Path) -> str:
        arquivo = Path(caminho)
        if arquivo.suffix.lower() != ".txt":
            raise ValueError("Apenas arquivos .txt sao aceitos.")
        self.conteudo = arquivo.read_text(encoding="utf-8")
        self.caminho = arquivo
        self.modificado = False
        return self.conteudo

    def atualizar_conteudo(self, conteudo: str) -> None:
        self.modificado = conteudo != self.conteudo
        self.conteudo = conteudo

    def salvar(self, caminho: str | Path | None = None) -> Path:
        destino = Path(caminho) if caminho is not None else self.caminho
        if destino is None:
            raise ValueError("Nenhum caminho de arquivo foi informado.")
        if destino.suffix.lower() != ".txt":
            raise ValueError("O texto deve ser salvo como arquivo .txt.")
        destino.write_text(self.conteudo, encoding="utf-8")
        self.caminho = destino
        self.modificado = False
        return destino
