import translationstring


TranslationStringFactory = translationstring.TranslationStringFactory('nativeview')


def simple_translator(term):
    if hasattr(term, 'interpolate'):
        return term.interpolate()
    return term


def default_translator(term):
    return _default_translator(term)


def set_default_translator(new_translator):
    global _default_translator
    _default_translator = new_translator


_default_translator = simple_translator
