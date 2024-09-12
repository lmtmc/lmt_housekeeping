#!/usr/bin/env python

import sys
venv_path = '/home/lmtmc_umass_edu/lmt_housekeeping/env'
sys.path.insert(0, venv_path)

import site
site.addsitedir(venv_path)

sys.path.insert(0, '/home/lmtmc_umass_edu/lmt_housekeeping')

from app import app
server = app.server