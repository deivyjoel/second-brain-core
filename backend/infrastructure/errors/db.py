class DBError(Exception):
    pass

class RepositoryError(DBError):
    pass

class UniqueConstraintViolation(DBError):
    pass

