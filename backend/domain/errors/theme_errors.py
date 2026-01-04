class ThemeDomainError(Exception):
    pass

class InvalidThemeNameError(ThemeDomainError):
    pass

class DuplicateThemeNameError(ThemeDomainError):
    pass

class InvalidThemeHierarchyError(ThemeDomainError):
    pass

