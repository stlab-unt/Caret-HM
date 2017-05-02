#!/usr/bin/env python

import json
import sys
import os
import misc
import glob
import itertools
import warnings
import PIL
import io
import cluster

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

warnings.filterwarnings("ignore")


#from pprint import pprint as pp

# convert a coordinate
def coord_convert(coord, y = None):

    maxX = maxY = 32767.0 # current maximum coordinate value of emulator
    minX = minY = 0.0 # current minimum --------------------------------
    displayWidth = 480.0 # current x resolution of emulator
    displayHeight = 800.0 # current y ---------------------

    # convert a coordinate according to its axis
    if y == 'y' or y == 1:
        res = displayHeight - (coord - minY) * displayHeight / (maxY - minY + 1.0)
    else:
        res = (coord - minX) * displayWidth / (maxX - minX + 1.0)

    # return coordinate
    return int(res)

# create a plot from data
def plot_data(app, d):
    # get unique groups
    state_uniq = [ dt for dt in d.c.unique() ]

    imgs = {}
    # for each group create a heatmap
    for a in state_uniq:
        dd = d[d['c'] == a]
        #plt.clf()
        plt.rc("figure", figsize=(4.8,8), frameon=False)
        fig = plt.figure(frameon=False)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        ax.axis('off')
        fig.add_axes(ax)
        fig.patch.set_visible(False)
        colors = [(1,0,0,i) for i in np.linspace(0,1,20)]
        cmap = mcolors.LinearSegmentedColormap.from_list('mycmap', colors, N=20)
        hx = ax.hexbin(dd['x'].values, dd['y'].values, gridsize=27, cmap=cmap, extent=[0,480,0,800])
        imgs[a] = io.BytesIO()
        ax.annotate(s="Taps: "+str(len(dd)), xy=(0,1), xytext=(5,770), color='red')
        plt.axis([0,480,0,800])
        plt.savefig(imgs[a], transparent=True)
        fig.clf()
        plt.clf()
        plt.close('all')
    return imgs

# combine heatmap and underlying image
def save_data(app, d, app_cluster, config):

    imgs = plot_data(app, d)
    img_list = []

    # process each image in images
    for i in imgs:
        imgs[i].seek(0)

        # get a state with the maximum number of elements (use it as a primary source for an image)
        mx = max(app_cluster[1][i], key=lambda x: len(x[4]))
        # get the first image in the state
        ss = next(iter(app_cluster[0][mx][1]))

        # get image name
        dname = ss[1].replace('.json','')
        fname = config['test_dir']+'/'+app+'/'+dname+'/'+ss[0]+'.png'

        # open background image and heatmap
        try:
            img = PIL.Image.open(config['test_dir']+'/'+app+'/'+dname+'/'+ss[0]+'.png')
            heatmap = PIL.Image.open(imgs[i])
        except:
            sys.exit(-1)

        # combine two images
        img.paste(heatmap, (0, 0), heatmap)
        img_loc = config['image_dir']+'/'+app+'-'+str(i)+'.png'
        # save it to image directory
        img.save(img_loc)
        img_list.append(img_loc)

    return img_list


def create_heatmaps(app, config):

    # get clusters
    clusters = cluster.cluster_tests(app, config)

    arr = []
    states = clusters[app][0]
    files = glob.glob(config['test_dir']+'/'+app+'/*.json')

    na_max = 0
    na_avg = 0
    na_min = 9999999999999999999999999999999999
    observed_activities = set()
    observed_elements = {}

    # get all sessions in apps
    for fn in files:
        data = json.load(open(fn))
        x = y = 0

        n_actions = len([i for i in data if i['command'][0] != 0 and i['command'][2] == 0])
        if n_actions < na_min:
            na_min = n_actions
        if n_actions > na_max:
            na_max = n_actions
        na_avg += n_actions
        # group actions by timestamp
        for ts, group in itertools.groupby(data, lambda x: x['timestamp']):
            dump = None
            wi = None

            # extract coordinates as well as state information from the group
            for e in (i for i in group if i['command'][0] == 3):

                # extract state if available
                if e['dump']:
                    dump = e['dump']
                    wi = e['window_info']

                # extract x or y coordinates
                elif e['command'][1] == 53:
                    x = coord_convert(e['command'][2])
                elif e['command'][1] == 54:
                    y = coord_convert(e['command'][2], 1)

            # if dump is not empty
            if dump:
                # get activity
                state = misc.process_wi(wi)
                # add activity to calculate the number of observed activities
                observed_activities.add(state)
                # get and add state
                state += (misc.get_all_xpaths(dump), )

                # append coordinate and cluster information to array
                arr.append({'c': states[state][0], 'x': x, 'y': y})

                # find element using boundaries of xml elements
                el = misc.get_element_by_boundaries(dump, x, y)

                # increment the number of times element was accessed
                if el:
                    if el in observed_elements:
                        observed_elements[el] += 1
                    else:
                        observed_elements[el] = 1

    data = pd.DataFrame(arr)
    state_uniq = [ dt for dt in data.c.unique() ]

    c_info = []
    for c in sorted(state_uniq):
        dd = data[data['c'] == c]
        c_info.append({
            'desc' : 'Taps in cluster '+str(c+1),
            'value': len(dd)
        })
    img_list = save_data(app, data, clusters[app], config)
    # return image list + basic statistic information
    return {
        'images': img_list,
        'stats': [
                    {
                        'desc': 'App name',
                        'value': app
                    }, {
                    }, {
                        'desc': 'Number of tests',
                        'value': len(files)
                    }, {
                        'desc':'Number of observed activities',
                        'value': len(observed_activities)
                    }, {
                        'desc':'Number of observed states',
                        'value': len(states)
                    }, {
                        'desc':'Number of generated clusters',
                        'value': len(img_list)
                    }, {
                    }, {
                        'desc':'Minimum number of actions in user session',
                        'value': na_min
                    }, {
                        'desc':'Average number of actions per user session',
                        'value': na_avg/len(files)
                    }, {
                        'desc':'Maximum number of actions in user session',
                        'value': na_max
                    }, {}
        ] + c_info + [{} ] + [ { 'desc': k, 'value': observed_elements[k] } for k in observed_elements ]
    }
