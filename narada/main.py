import os
import sys
import time

from flask import Flask, request
from flask_restful import Resource, Api

def main(port=2020):
    try:
        import signal
        import sys
        def signal_handler(sig, frame):
                print('Exiting...')
                sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)
        from narada import launch_service
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        launch_service(port)
    except Exception as e:
        # The following sleep is to accommodate a common IDE issue of
        # interspersing main exception with console output.
        time.sleep(0.5)
        msg = '''
    {0}
    Sorry. Looks like this is an error Narada couldn't handle.
    Create a bug report on GitHub: https://github.com/rahul-verma/narada
    {0}

    Message: {1}
        '''.format("-" * 70, str(e))
        print(msg)
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import sys, os
    my_dir = os.path.dirname(os.path.realpath(__file__))
    narada_dir = os.path.join(my_dir, "..")
    sys.path.append(narada_dir)
    main()
