from wizlib.app import WizApp
from wizlib.stream_handler import StreamHandler
from wizlib.config_handler import ConfigHandler
from wizlib.ui_handler import UIHandler

from flutterby.command import FlutterbyCommand


class FlutterbyApp(WizApp):

    base = FlutterbyCommand
    name = 'template'
    handlers = [StreamHandler, ConfigHandler, UIHandler]
