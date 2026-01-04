from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.infrastructure.repositories.sql_alchemy import models
from backend.infrastructure.repositories.note_repository import NoteRepository
from backend.infrastructure.repositories.theme_repository import ThemeRepository
from backend.infrastructure.repositories.time_repository import TimeRepository
from backend.infrastructure.repositories.analytics_repository import AnalyticsRepository
from backend.infrastructure.repositories.search_efficiency_repository import SearchEfficiencyRepository

from backend.application.backend_api import BackendAPI
from frontend.gui_main import Gui
from frontend.core.api_provider import ApiProvider



# --- DB setup ---
engine = create_engine('sqlite:///app.db', echo=False)
models.Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
nt_repo = NoteRepository(session)
thm_repo = ThemeRepository(session)
tm_repo = TimeRepository(session)
an_repo = AnalyticsRepository(session)
sc_repo = SearchEfficiencyRepository(session)
back_api = BackendAPI(nt_repo, thm_repo, tm_repo, an_repo, sc_repo)
ApiProvider.set(back_api)


# -------------------
if __name__ == "__main__":
    app = Gui()
    app.run()
