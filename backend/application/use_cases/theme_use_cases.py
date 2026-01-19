from datetime import datetime, timezone

from backend.infrastructure.repositories.theme_repository import ThemeRepository
from backend.infrastructure.repositories.analytics_repository import AnalyticsRepository
from backend.infrastructure.repositories.search_efficiency_repository import SearchEfficiencyRepository

from backend.application.decorators.usecase_guard import handle_usecase_errors
from backend.application.dto.theme_details_dto import ThemeDetailDTO
from backend.application.results.operation_result import OperationResult
from backend.application.dto.theme_summary_dto import ThemeSummaryDTO
from backend.application.services.analyzer_services import AnalyzerService
from backend.application.dto.theme_analytics_dto import ThemeAnalyticsDTO
from backend.application.services.theme_services import ThemeService

from backend.domain.models.theme import Theme



# --- OPERATIONS ---
@handle_usecase_errors
def create_theme(
    theme_repo: ThemeRepository,
    theme_service: ThemeService,
    name: str, 
    parent_id: int | None = None
    ) -> OperationResult[int]:    
    sibling_names = theme_service.get_names_in_theme_id(parent_id)
    theme = Theme.create(name, sibling_names=set(sibling_names), parent_id=parent_id)
    id_theme = theme_repo.add(theme)
            
    return OperationResult(True, "Tema creado exitosamente", id_theme)

@handle_usecase_errors
def delete_theme(theme_repo: ThemeRepository, theme_id: int) -> OperationResult[None]:
    theme = theme_repo.get_by_id(theme_id)
    if not theme:
        return OperationResult(False, "No se pudo eliminar el tema porque no existe", None)
    theme_repo.delete(theme_id)
    return OperationResult(successful=True, 
                                info="Se eliminó correctamente el tema",
                                obj=None)            

@handle_usecase_errors
def delete_many_themes(theme_repo: ThemeRepository, theme_ids: list[int]) -> OperationResult[None]:
    theme_repo.delete_many(theme_ids)
    return OperationResult(True, "Temas eliminados correctamente", None)


@handle_usecase_errors
def rename_theme(theme_repo: ThemeRepository,
                 theme_service: ThemeService, 
                theme_id: int, new_name: str) -> OperationResult[None]:
    theme = theme_repo.get_by_id(theme_id)
    if not theme:
        return OperationResult(False, "No se pudo renombrar el tema porque no existe", None)

    names_in_theme = theme_service.get_names_in_theme_id(theme._parent_id)
    #UTC
    now = datetime.now(timezone.utc)
    theme.change_name(new_name, set(names_in_theme), now)
    theme_repo.update(theme)
    return OperationResult(successful=True, info="Se cambió el nombre del tema correctamente", obj=None)


@handle_usecase_errors
def remove_theme(theme_repo: ThemeRepository,
                           theme_service: ThemeService,
                           theme_id: int, 
                           search_repo: SearchEfficiencyRepository,
                           new_parent_id: int | None = None
                           ) -> OperationResult[None]:
    theme = theme_repo.get_by_id(theme_id)
    if not theme:
        return OperationResult(False, "No se pudo cambiar el tema padre del tema hijo porque el tema hijo no existe", None)

    if new_parent_id is not None:
        parent_theme = theme_repo.get_by_id(new_parent_id)
        if not parent_theme:
            return OperationResult(False, "No se pudo cambiar el tema padre del tema hijo porque el tema padre es inexistente", None)
        
    names_in_theme = theme_service.get_names_in_theme_id(new_parent_id)
    descendients = set(search_repo.get_theme_descendants_ids(theme_id))

    theme.change_parent_id(new_parent_id, set(names_in_theme), descendients)
    theme_repo.update(theme)
    return OperationResult(successful=True, info="Se cambió el padre del tema correctamente", obj=None)


# ------ QUERIES -----
@handle_usecase_errors
def get_unique_theme_name(
                    theme_repo: ThemeRepository,
                    theme_service: ThemeService,
                    name: str, theme_id: int | None = None) -> OperationResult[str]:
    if theme_id:
        theme = theme_repo.get_by_id(theme_id)
        if not theme:
            return OperationResult(False, "No se pudo obtener un unico nombre para el tema porque el tema dado no existe", None)
    u_name = theme_service.get_unique_name_for_theme(name, theme_id)
    return OperationResult(True, "", u_name)

@handle_usecase_errors
def get_themes_descendants(theme_id: int, search_repo: SearchEfficiencyRepository) -> OperationResult[list[int]]:
    ids_notes = search_repo.get_theme_descendants_ids(theme_id)
    return OperationResult(True, "", ids_notes)

@handle_usecase_errors
def get_theme_details(theme_repo: ThemeRepository, 
              theme_id: int
              ) -> OperationResult[ThemeDetailDTO]:
    theme = theme_repo.get_by_id(theme_id)
    if not theme:
        return OperationResult(False, "No se pudo obtener los detalles del tema porque no existe", None)
    theme_dto = ThemeDetailDTO(
        theme_id = theme._id,
        name = theme._name,
        parent_id = theme._parent_id
    )

    return OperationResult(successful=True, 
                                info="Se eliminó correctamente el tema",
                                obj=theme_dto)            
 
@handle_usecase_errors
def list_themes(theme_repo: ThemeRepository) -> OperationResult[list[ThemeSummaryDTO]]:
    themes = theme_repo.get_all_themes()
    themes_dto = [ThemeSummaryDTO(
        id = t._id,
        name = t._name
    ) for t in themes if t._id]
    return OperationResult(successful=True, 
                                info="Temas listados correctamente",
                                obj=themes_dto)            

@handle_usecase_errors
def list_child_themes(
    theme_repo: ThemeRepository, 
    parent_id: int
    ) -> OperationResult[list[ThemeSummaryDTO]]:
    theme = theme_repo.get_by_id(parent_id)
    if not theme:
        return OperationResult(False, "No se pudo listar los temas hijos del tema padre porque el tema padre no existe", None)
    themes = theme_repo.get_themes_by_parent_id(theme_id=parent_id)
    themes_dto = [ThemeSummaryDTO(
        id = t._id,
        name = t._name
    ) for t in themes if t._id]
    return OperationResult(successful=True, 
                                info=f"Temas del padre {parent_id} listados correctamente",
                                obj=themes_dto)         
      
@handle_usecase_errors
def list_root_themes(theme_repo: ThemeRepository) -> OperationResult[list[ThemeSummaryDTO]]:
    themes = theme_repo.get_themes_without_parent_id()
    themes_dto = [ThemeSummaryDTO(
        id = t._id,
        name = t._name
    ) for t in themes if t._id]
    return OperationResult(True, f"Temas sin padre listados correctamente",
                               obj=themes_dto)     

@handle_usecase_errors
def get_theme_analytics(analy_repo: AnalyticsRepository,
                      search_repo: SearchEfficiencyRepository,
                      theme_repo: ThemeRepository, 
                      analyzer_service: AnalyzerService,
                      theme_id: int) -> OperationResult[ThemeAnalyticsDTO]:
    
    theme = theme_repo.get_by_id(theme_id)
    if not theme:
        return OperationResult(False, "No se pudo obtener las analiticas del tema porque el tema dado es inexistente", None)
    descendants = search_repo.get_theme_descendants_ids(theme_id)
    raw_stats = analy_repo.get_time_and_note_counts(descendants, theme_id)
    n_notes_directly = analy_repo.count_direct_notes(theme_id)
    n_entities = raw_stats.total_notes + raw_stats.n_subthemes
    content_total = analy_repo.get_aggregated_content(descendants, theme_id)
    n_meaningful = analyzer_service.count_meaningful(content_total)
    n_unique = analyzer_service.count_unique(content_total)

    theme_analytics = ThemeAnalyticsDTO(
        name=theme._name,
        created_at=theme._created_at,
        last_edited_at=theme._last_edited_at,
        minutes_total=raw_stats.minutes,
        n_notes_directly=n_notes_directly,
        n_entities=n_entities,
        n_days_active=raw_stats.active_days,
        n_content_words_total=n_meaningful,
        n_u_content_words_totals=n_unique
    )

    return OperationResult(True, "Success", obj=theme_analytics)