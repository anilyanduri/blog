# run.py
"""App runner for blog.

Usage:
  run.py [options]

  -c --console                            Run app py console
"""

import os
from docopt import docopt

from blog import create_app

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    if arguments["--console"]:
        app.cli()
    else:
        app.run()

