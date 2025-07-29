import sys
import click

from PySide6.QtWidgets import QApplication

from .liteboty_stream import MainWindow as StreamMainWindow
from .liteboty_stream_ui import StreamUI


@click.group()
def cli():
    pass


@cli.command()
@click.option('--broker', required=True, help="Redis broker address (e.g., 10.8.2.2:6379)")
@click.option('--decode', default='RGB', help="Image decode format (e.g., RGB, L)")
@click.option('--channel', required=True, help="Redis channel to subscribe to (e.g., /video/raw)")
def run(broker, decode, channel):
    app = QApplication(sys.argv)
    window = StreamMainWindow(broker, channel, decode)
    window.show()
    sys.exit(app.exec())


@cli.command()
def ui():
    app = QApplication(sys.argv)
    window = StreamUI()
    window.show()
    sys.exit(app.exec())
