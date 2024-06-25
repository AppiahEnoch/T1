import sys

def pause_on_error():
    if hasattr(sys, 'frozen') and hasattr(sys, 'exit'):
        import traceback
        try:
            sys.excepthook = lambda exctype, value, tb: (traceback.print_exception(exctype, value, tb), input('Press Enter to exit...'), sys.exit(1))
        except:
            pass

pause_on_error()
