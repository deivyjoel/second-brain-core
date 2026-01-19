class ImageDomainError(Exception):
    pass

class InvalidImageNameError(ImageDomainError):
    pass

class DuplicateImageNameError(ImageDomainError):
    pass

class InvalidImageExtensionError(ImageDomainError):
    pass
