from frontend.core.bus import Bus
from frontend.features.anaylitics_feature import AnalyticsWindow
from frontend.core.api_provider import ApiProvider

class AnalyticsManager:
    """Responsible for creating the visual interface to display analytics."""
    def __init__(self):
        self.api = ApiProvider.get()
        Bus.subscribe("OPEN_DETAILS_ITEM", self._show_analytics)

    def _show_analytics(self, dto_analytics):
        new_view = AnalyticsWindow(dto_analytics)
        new_view.lift()         
        new_view.focus_force()   
