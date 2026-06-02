from pathlib import Path


class ReprodutorMusical:
    def __init__(self) -> None:
        self._inicializado = False

    def _garantir_inicializado(self) -> None:
        if self._inicializado:
            return
        try:
            import pygame

            pygame.mixer.init()
        except Exception as erro:
            raise RuntimeError(f"Falha ao inicializar pygame: {erro}") from erro
        self._inicializado = True

    def reproduzir(self, caminho_midi: str | Path) -> None:
        self._garantir_inicializado()
        try:
            import pygame

            pygame.mixer.music.load(str(caminho_midi))
            pygame.mixer.music.play()
        except Exception as erro:
            raise RuntimeError(f"Falha ao reproduzir MIDI: {erro}") from erro

    def pausar(self) -> None:
        self._garantir_inicializado()
        import pygame

        pygame.mixer.music.pause()

    def retomar(self) -> None:
        self._garantir_inicializado()
        import pygame

        pygame.mixer.music.unpause()

    def parar(self) -> None:
        if not self._inicializado:
            return
        import pygame

        pygame.mixer.music.stop()
        