from i18n import default_translator


__all__ = ['ValidationError']


def translate(detail):
    if isinstance(detail, list):
        new_detail = []
        for subdetail in detail:
            new_detail.append(translate(subdetail))
        return new_detail
    elif isinstance(detail, dict):
        new_detail = {}
        for key, subdetail in detail.iteritems():
            new_detail[key] = translate(subdetail)
        return new_detail
    else:
        return default_translator(detail)


class ValidationError(Exception):
    def __init__(self, detail, unit=None):
        """
        :detail: str, list or dict.
        """
        if not isinstance(detail, (dict, list)):
            detail = [detail]
        self._detail = detail
        self.unit = unit

    @property
    def detail(self):
        return translate(self._detail)

    def __str__(self):
        return self.detail
