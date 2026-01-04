from functools import wraps
from backend.domain.errors.note_errors import NoteDomainError
from backend.infrastructure.errors.db import DBError
from backend.application.results.operation_result import OperationResult
from backend.domain.errors.note_errors import NoteDomainError
from backend.domain.errors.theme_errors import ThemeDomainError

from pydantic import ValidationError
from backend.application.decorators.validator import validate_types


def handle_usecase_errors(f):
    f_validated = validate_types(f)
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f_validated(*args, **kwargs)
        
        except ValidationError as e:
            errors = e.errors()
            campo = errors[0].get('loc', ('desconocido',))[-1] 
            detalle = errors[0].get('msg', 'Error de validación')
            
            msg = f"Dato inválido en '{campo}': {detalle}"
            return OperationResult(False, msg, None)
        
        except NoteDomainError as e:
            return OperationResult(False, str(e), None)
        
        except ThemeDomainError as e:
            return OperationResult(False, str(e), None)
        
        except DBError:
            return OperationResult(False, "Error de base de datos", None)
        
        except Exception:
            return OperationResult(False, "Ocurrió un error interno", None)
        
    return wrapper

