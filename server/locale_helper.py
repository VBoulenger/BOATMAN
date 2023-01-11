import contextlib
import locale


@contextlib.contextmanager
def locale_context(requested_locale: str):
    saved = locale.getlocale()
    try:
        locale.setlocale(locale.LC_ALL, requested_locale)
        yield requested_locale
    finally:
        locale.setlocale(locale.LC_ALL, saved)
