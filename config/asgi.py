import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import config.routing

application = config.routing.application
