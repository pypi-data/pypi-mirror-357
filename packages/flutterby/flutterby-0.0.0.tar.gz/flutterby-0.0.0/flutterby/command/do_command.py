from wizlib.parser import WizParser

from flutterby.command import FlutterbyCommand


class DoCommand(FlutterbyCommand):
    """Do something"""

    name = 'do'

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        # parser.add_argument()

    def handle_vals(self):
        super().handle_vals()
        # if not self.provided('dir'):
        #     self.dir = self.app.config.get('filez4eva-source')

    @FlutterbyCommand.wrap
    def execute(self):
        self.status = 'Done'
        return "Hello, World!"
