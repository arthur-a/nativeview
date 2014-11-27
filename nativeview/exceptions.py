__all__ = ['ValidationError']


class ValidationError(Exception):
    def __init__(self, detail, unit=None):
        """
        :detail: str, list or dict.
        """
        if not isinstance(detail, (dict, list)):
            detail = [detail]
        self.detail = detail
        self.unit = unit

    def __str__(self):
        return self.detail
