#!/usr/bin/env python

import glob
from app import process

def get_apps(config):
    return sorted(a.replace(config['test_dir']+'/','') for a in glob.glob(config['test_dir']+'/*'))

def make_heatmaps(app, config):
    return process.create_heatmaps(app, config)
