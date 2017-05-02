#!/usr/bin/env python

import glob
import os
import sys
import shutil
import json
import misc
import itertools
import hashlib
import numpy as np
import sklearn.cluster as cluster

# from pprint import pprint as pp
# np.set_printoptions(threshold=np.nan, linewidth=400, precision=4)

# distance edit function
def compare_tuple(t1, t2, ratio):

    # if mCurrentFocus or mFocusedApp differ -> distance = 1
    for a in xrange(0,4):
        if t1[a] != t2[a]:
            return 1

    # if ratio is 0, no state distance is calculated
    if not ratio:
        return 0

    # otherwise, distance is Jaccard Index
    t_intersection = float(len(t1[4] & t2[4]))
    t_union  = float(len(t1[4] | t2[4]))

    # return normalized Jaccard Index * distance ratio
    return (1.0-(t_intersection/t_union))*ratio


# create a distance matrix from states
def edit_distance(state_list, dratio):
    dmat = np.zeros((len(state_list),len(state_list)))
    for i1, i2 in itertools.combinations(xrange(len(state_list)), 2):
        cmp_tpl = compare_tuple(state_list[i1],state_list[i2], dratio)
        dmat[i1, i2] = cmp_tpl
        dmat[i2, i1] = cmp_tpl
    #sys.exit(0)
    return dmat


# cluster existing states using agglomerative clustering and distance matrix
def cluster_states(dmat, lact, config):
    if config['number_type'] == 'ratio':
        num_clusters = int(lact*config['number_value'])
    else:
        num_clusters = int(config['number_value'])
    if num_clusters > len(dmat):
        num_clusters = len(dmat)
    clustering = cluster.AgglomerativeClustering(n_clusters = max(2, num_clusters), affinity = 'precomputed', linkage = config['linkage'])
    #clustering = cluster.DBSCAN(eps=0.1, metric='precomputed')
    return clustering.fit_predict(dmat)


# process files in the directory and extract all available states
def get_states(dname, config):
    state = set()
    activities = set()
    ts_state = {}

    # open user sessions at the directory
    for fn in glob.glob(dname+'/*.json'):
        test = json.load(open(fn))
        # process each action that has state
        for e in (i for i in test if i['dump']):

            # extract mFocusedApp/mCurrentFocus from window info dump
            entry = misc.process_wi(e['window_info'])
            activities.add(entry)

            # continue constructing current state
            entry = entry + (misc.get_all_xpaths(e['dump']),)

            # add state to the set of states
            state.add(entry)

            # preserve state's timestamp and the name of the user session file
            # (only one at the moment)
            if entry not in ts_state:
                ts_state[entry]=set()
            ts_state[entry].add(('{:.6f}'.format(e['timestamp']), os.path.basename(fn)))

    # generate distance matrix
    state_list = list(state)
    ed_mat = edit_distance(state_list, config['distance_ratio'])
    lact = len(activities)

    # cluster states using a simple way heuristic to for a number of clusters
    # the number of clusters is minimum of activity ratio or maximum clusters
    cl_states = cluster_states(ed_mat, lact, config)

    states = {}

    # group states into clusters
    for idx, c in enumerate(cl_states):
        if c not in states:
            states[c] = []
        states[c].append(state_list[idx])
        ts_state[state_list[idx]] = (c, ts_state[state_list[idx]])

    # return states and preserved timestamps/filenames
    return ts_state, states


def cluster_tests(app, config):

    complete_states = {}

    # read directory names in the given directory
    for dn in glob.glob(config['test_dir']+'/'+app):
        app = os.path.basename(dn)
        complete_states[app] = get_states(dn, config)

    return complete_states
