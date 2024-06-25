import threading

def run_in_thread(func, *args, **kwargs):
    """
    Run a given function in a separate thread.
    
    :param func: The function to run in a separate thread.
    :param args: Positional arguments to pass to the function.
    :param kwargs: Keyword arguments to pass to the function.
    """
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.start()
    return thread


