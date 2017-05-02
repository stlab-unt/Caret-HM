#!/bin/env python

import glob

# a service function to check if a string is a float (not needed atm)
def is_float(self, value):

    try:
        float(value)
        return True

    except ValueError:
        return False

# get a list of available apps
def get_apps():
    return sorted(glob.glob("conf/*.json"))

# merge json config files
def json_merge(a, b):

    try:
        if isinstance(a, list):
            if isinstance(b, list):
                a.extend(b)
            else:
                a.append(b)

        elif isinstance(a, dict):
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = json_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise InputError('Cannot merge non-dict "%s" into dict "%s"' % (b, a))

        else:
            a = b

    except TypeError, e:
        raise Error('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))

    return a