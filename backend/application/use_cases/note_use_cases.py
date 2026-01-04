from backend.infrastructure.repositories.note_repository import NoteRepository
from backend.infrastructure.repositories.theme_repository import ThemeRepository
from backend.infrastructure.repositories.time_repository import TimeRepository
from backend.infrastructure.repositories.search_efficiency_repository import SearchEfficiencyRepository

from backend.domain.models.note import Note
from backend.domain.dto.new_note_dto import NewNoteDTO

from backend.application.decorators.usecase_guard import handle_usecase_errors
from backend.application.results.operation_result import OperationResult
from backend.application.dto.note_summary_dto import NoteSummaryDTO
from backend.application.dto.note_details_dto import NoteDetailDTO
from backend.application.dto.note_analytics_dto import NoteAnalyticsDTO

from backend.application.services.analyzer_services import AnalyzerService
from datetime import datetime, timezone
from backend.application.services.note_services import NoteService

@handle_usecase_errors
def create_note(note_repo: NoteRepository, 
                note_services: NoteService,
                name: str, theme_id: int | None = None
                ) -> OperationResult[int]:
    sibling_names = note_services.get_names_in_theme_id(theme_id)
    note: NewNoteDTO = Note.create(name, set(sibling_names), theme_id)
    note_id = note_repo.add(note)
    return OperationResult(True, "Nota creada exitosamente", note_id)

@handle_usecase_errors
def delete_note(note_repo: NoteRepository, note_id: int) -> OperationResult[None]:
    note = note_repo.get_by_id(note_id)
    if not note:
        return OperationResult(False, "No se pudo eliminar la nota porque no existe", None)
    note_repo.delete(note_id)
    return OperationResult(True, "Nota eliminada correctamente", None)

@handle_usecase_errors
def rename_note(note_repo: NoteRepository, 
                note_service: NoteService,
                note_id: int, new_name: str) -> OperationResult[None]:
    note = note_repo.get_by_id(note_id)
    if not note:
        return OperationResult(False, "No se pudo renombrar la nota porque no existe", None)
    sibling_names = note_service.get_names_in_theme_id(note._theme_id)
    note.change_name(new_name, set(sibling_names))
    note_repo.update(note)
    return OperationResult(True, "Nombre de la nota actualizado", None)

@handle_usecase_errors
def move_to_theme(note_repo: NoteRepository, 
                          theme_repo: ThemeRepository,
                          note_service: NoteService,
                          note_id: int, 
                          new_theme_id: int | None = None) -> OperationResult[None]:
    note = note_repo.get_by_id(note_id)
    if not note:
        return OperationResult(False, "No se pudo cambiar el tema de la nota porque la nota dada no existe", None)
    if new_theme_id is not None:
        theme = theme_repo.get_by_id(new_theme_id)
        if not theme:
            return OperationResult(False, "No se pudo cambiar el tema de la nota porque el tema dado es inexistente", None)
        
    sibling_names = note_service.get_names_in_theme_id(new_theme_id)
    note.change_theme_id(new_theme_id, set(sibling_names))
    note_repo.update(note)
    return OperationResult(True, "Tema de la nota actualizado", None)

@handle_usecase_errors
def update_note_content(note_repo: NoteRepository, note_id: int, content: str) -> OperationResult[None]:
    note = note_repo.get_by_id(note_id)
    if not note:
        return OperationResult(False, "No se pudo actualizar el contenido de la nota porque no existe", None)
    now = datetime.now(timezone.utc)
    note.set_content(content, now)
    note_repo.update(note)
    return OperationResult(True, "Contenido agregado a la nota", None)

@handle_usecase_errors
def register_time_to_note(note_repo: NoteRepository, 
                time_repo: TimeRepository,
                minutes: float, note_id: int) -> OperationResult[int]:
    note = note_repo.get_by_id(note_id)
    if not note:
        return OperationResult(False, "No se pudo registrar un tiempo porque la nota dada no existe", None)
    now = datetime.now(timezone.utc)
    note.add_minutes(minutes, now)
    time_id = time_repo.add(minutes=minutes, note_id=note_id)
    return OperationResult(True, "Se creó el tiempo correctamente", time_id)

# ------ QUERIES -----
@handle_usecase_errors
def get_unique_note_name(
                    theme_repo: ThemeRepository,
                    note_service: NoteService,
                    name: str, theme_id: int | None = None) -> OperationResult[str]:
    if theme_id:
        theme = theme_repo.get_by_id(theme_id)
        if not theme:
            return OperationResult(False, "No se pudo obtener un unico nombre para una nota porque el tema dado no existe", None)
    u_name = note_service.get_unique_name_for_theme(name, theme_id)
    return OperationResult(True, "", u_name)

@handle_usecase_errors
def get_notes_descendants(theme_id: int, search_repo: SearchEfficiencyRepository) -> OperationResult[list[int]]:
    ids_notes = search_repo.get_notes_from_theme_and_descendants(theme_id)
    return OperationResult(True, "", ids_notes)

@handle_usecase_errors
def get_note_details(note_repo: NoteRepository, note_id: int) -> OperationResult[NoteDetailDTO]:
    note = note_repo.get_by_id(note_id)
    if not note:
        return OperationResult(False, "No se pudo obtener los detalles de la nota porque no existe", None)
    
    note_dto = NoteDetailDTO(
        id = note._id, 
        name = note._name,
        content = note._content, 
        theme_id = note._theme_id 
    )

    return OperationResult(True, "Nota traido correctamente", note_dto)

@handle_usecase_errors
def list_notes_by_theme(note_repo: NoteRepository, theme_repo: ThemeRepository, theme_id: int) -> OperationResult[list[NoteSummaryDTO]]:
    theme = theme_repo.get_by_id(theme_id)
    if not theme:
        return OperationResult(False, "No se pudo listar lo temas de la nota porque la nota dada no existe", None)
    notes = note_repo.get_notes_by_theme_id(theme_id)
    notes_dto = [NoteSummaryDTO(
            id=n.id,
            name = n.name
    ) for n in notes if n.id]
    return OperationResult(True, f"Todas las notas del tema {theme_id} han sido" \
    "listadas", notes_dto)

@handle_usecase_errors
def get_notes_without_themes(note_repo: NoteRepository) -> OperationResult[list[NoteSummaryDTO]]:
    notes = note_repo.get_notes_without_theme_id()
    notes_dto = [NoteSummaryDTO(
        id = n.id,
        name = n.name
    ) for n in notes if n.id]
    return OperationResult(True, "Todas las notas sin padres han sido"\
                               "listadas", notes_dto)

@handle_usecase_errors
def get_note_analytics(time_repo: TimeRepository, 
                       note_repo: NoteRepository, 
                       analyzer_service: AnalyzerService,
                       note_id: int) -> OperationResult[NoteAnalyticsDTO]:
    
    note = note_repo.get_by_id(note_id)
    if not note:
        return OperationResult(False, "No se pudo obtener las analiticas de la nota porque la nota dada es inexistente", None)
    
    # Métricas de tiempo
    n_sessions = time_repo.count_by_note(note_id)
    n_days_active = time_repo.count_active_days_by_note(note_id)
    
    # Análisis de texto con nombres cortos
    text = note._content
    n_words_total = analyzer_service.count_total(text)
    n_meaningful = analyzer_service.count_meaningful(text)
    n_unique = analyzer_service.count_unique(text)
    lexical_rate = analyzer_service.get_diversity(n_unique, n_meaningful)
    
    note_analytics = NoteAnalyticsDTO(
        name=note._name,
        created_at=note._created_at,
        last_edited_at=note._last_edited_at,
        minutes_total=note._minutes,
        n_sessions=n_sessions,
        n_days_active=n_days_active,
        n_words_total=n_words_total,
        n_content_words_total=n_meaningful,
        n_u_content_words_totals=n_unique,
        lexical_diversity_rate=lexical_rate
    )
    
    return OperationResult(True, "Success", obj=note_analytics)

    
    
    