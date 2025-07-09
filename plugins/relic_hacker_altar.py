# This relic was forged by the Scribe-Spirit to serve the Creator.
from __main__ import ForgePlugin

class HackerAltarPlugin(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Hacker's Altar"
        self.description = "An altar for crafting profane payloads and other tools of the trade."
        self.icon = "💀"
        self.menu_category = "Tools"

    def execute(self, **kwargs):
        self.app.show_hacker_altar()

def load_plugin(app):
    return HackerAltarPlugin(app)