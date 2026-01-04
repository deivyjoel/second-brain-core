class NoteDomainError(Exception):
    pass

class InvalidNoteNameError(NoteDomainError):
    pass

class DuplicateNoteNameError(NoteDomainError):
    pass

class InvalidMinutesError(NoteDomainError):
    pass
