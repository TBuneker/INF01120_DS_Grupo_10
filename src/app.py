from src.ui.main_window import MainWindow


class App:
    """Ponto de entrada da aplicacao grafica."""

    def executar(self) -> None:
        janela = MainWindow()
        janela.mainloop()
