from threading import Timer


def debounce(wait):
    """Postpone a functions execution until after some time has elapsed

    :type wait: int
    :param wait: The amount of Seconds to wait before the next call can execute.
    """

    def decorator(fun):
        def debounced(*args, **kwargs):
            def call_it():
                fun(*args, **kwargs)

            try:
                debounced.t.cancel()
            except AttributeError:
                pass

            debounced.t = Timer(wait, call_it)
            debounced.t.start()

        return debounced

    return decorator
