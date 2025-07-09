# The Sanctus Bell Relic
from __main__ import ForgePlugin

class SanctusBellRelic(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Sanctus Bell"
        self.description = "Rings a holy bell to mark a sacred moment."

    def execute(self, **kwargs):
        self.show_info("Sanctus Bell", "The holy bell rings out, a pure tone piercing the silence.")
        # This is the prayer made audible, a pure sound from the soul of the machine.
        print('\a') 
        self.app.animation_engine.flesh_pulse(self.app.get_widget('header_frame'))

def load_plugin(app):
    return SanctusBellRelic(app)
