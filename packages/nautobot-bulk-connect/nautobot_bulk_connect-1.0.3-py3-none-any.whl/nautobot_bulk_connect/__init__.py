from importlib import metadata

from nautobot.extras.plugins import PluginConfig

__version__ = metadata.version(__name__)


class ChangeConfig(PluginConfig):
    name = 'nautobot_bulk_connect'
    verbose_name = 'Bulk Connect'
    description = 'A plugin for bulk connect'
    version = __version__
    author = "Gesellschaft für wissenschaftliche Datenverarbeitung mbH Göttingen"
    author_email = "netzadmin@gwdg.de"
    base_url = 'nautobot-bulk-connect'
    required_settings = [
        'device_role'
    ]
    default_settings = {}
    middleware = []


config = ChangeConfig
