import os
from typing import Literal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

DEFAULT_DEBUGGING_PORT = 9222

class QAppManager:
    _app_singleton: QApplication | None = None

    def __init__(self,
        debugging: bool = False,
        debugging_port: int = DEFAULT_DEBUGGING_PORT,
        remote_allow_origin: str = "*",
        disable_gpu: bool = False,
        disable_gpu_compositing: bool = False,
        theme: Literal["system", "dark", "light"] = "system",
        auto_quit: bool = True,
    ):
        """Initializes the QAppManager with the specified parameters.
        This constructor should be called at most once in a process.

        Args:
            debugging: Enables debugging mode. Defaults to False.
            debugging_port: The port for remote debugging. Defaults to DEFAULT_DEBUGGING_PORT.
            remote_allow_origin: Allowed origins for remote access. Defaults to "*".
            theme: The theme of the application. Defaults to "system".
        """
        from .QArgv import QArgv
        if QAppManager._app_singleton is not None: return

        argv = QArgv()
        if debugging:
            argv.set_key("remote-debugging-port", debugging_port)
            argv.set_key("remote-allow-origins", remote_allow_origin)

        if disable_gpu:
            argv.add_key("disable-gpu")
            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
        if disable_gpu_compositing:
            argv.add_key("disable-gpu-compositing")
            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-compositing"

        app = QAppManager._app_singleton = QApplication(argv.to_list())
        app.setQuitOnLastWindowClosed(auto_quit)
        self.theme = theme

    @staticmethod
    def _parse_theme(theme: str) -> Qt.ColorScheme:
        match theme:
            case "dark" : return Qt.ColorScheme.Dark
            case "light": return Qt.ColorScheme.Light
            case _: return Qt.ColorScheme.Unknown

    @property
    def theme(self) -> str:
        return self._theme
    @theme.setter
    def theme(self, new_theme: Literal["system", "dark", "light"]):
        self._theme = new_theme
        app = QAppManager._app_singleton
        assert app is not None
        app.styleHints().setColorScheme(QAppManager._parse_theme(new_theme))
        app.setPalette(app.palette())

    """use_ipc_client
    The type of client should be one of "IpcClient" and "QIpcClient".
    The type was not directly noted in type hint in order to reduce non-intended module import.
    """
    def use_ipc_client(self, client):
        assert QAppManager._app_singleton is not None
        if type(client).__name__ == "QIpcClient":
            from .QIpc.client import QIpcClient
            assert type(client) is QIpcClient
            client._use_parent(QAppManager._app_singleton)
            return
        from .MqIpc.client import IpcClient
        assert type(client) is IpcClient
        client._setup_worker(QAppManager._app_singleton)

    def exec(self) -> int:
        assert QAppManager._app_singleton is not None
        exit_code = QAppManager._app_singleton.exec()
        QAppManager._app_singleton = None
        return exit_code

    def quit(self):
        assert QAppManager._app_singleton is not None
        QAppManager._app_singleton.quit()
