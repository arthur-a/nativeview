__all__ = ['preparer_chain']


def preparer_chain(*preparers):
    def inner(data):
        for preparer in preparers:
            data = preparer(data)
        return data
    return inner