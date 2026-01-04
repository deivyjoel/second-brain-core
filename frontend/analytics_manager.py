from frontend.core.bus import Bus
from frontend.features.anaylitics_feature import AnalyticsWindow
from frontend.core.api_provider import ApiProvider

class AnalyticsManager:
    def __init__(self):
        print("mmmm")
        self.api = ApiProvider.get()
        # El controlador escucha el evento global
        Bus.subscribe("OPEN_DETAILS_ITEM", self._show_analytics)

    def _show_analytics(self, dto_analytics):
        # Cuando llega el evento, el controlador "monta" la feature
        print("jkeje")
        new_view = AnalyticsWindow(dto_analytics)
        new_view.lift()         
        new_view.focus_force()   
