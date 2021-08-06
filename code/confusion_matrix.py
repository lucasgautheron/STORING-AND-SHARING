#!/usr/bin/env python3

from ChildProject.projects import ChildProject
from ChildProject.annotations import AnnotationManager
from ChildProject.metrics import gamma, segments_to_grid

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import normalize

import seaborn as sns
import matplotlib.pyplot as plt

import sys

speakers = ['CHI', 'OCH', 'FEM', 'MAL']

path = sys.argv[1]
project = ChildProject(path)
am = AnnotationManager(project)
am.read()

intersection = AnnotationManager.intersection(am.annotations, ['vtc', 'its'])
segments = am.get_collapsed_segments(intersection)
segments = segments[segments['speaker_type'].isin(speakers)]

vtc = segments_to_grid(segments[segments['set'] == 'vtc'], 0, segments['segment_offset'].max(), 100, 'speaker_type', speakers)
its = segments_to_grid(segments[segments['set'] == 'its'], 0, segments['segment_offset'].max(), 100, 'speaker_type', speakers)

speakers.extend(['overlap', 'none'])

def grid_to_vector(grid):
    return np.argmax(grid[:,::-1], axis = 1)

def conf_matrix(horizontal, vertical, categories):
    n = len(categories)-1
    vertical = np.vectorize(lambda x: categories[n-x])(grid_to_vector(vertical))
    horizontal = np.vectorize(lambda x: categories[n-x])(grid_to_vector(horizontal))

    confusion = confusion_matrix(vertical, horizontal, labels = categories)
    confusion = normalize(confusion, axis = 1, norm = 'l1')

    return confusion

plt.rcParams.update({'font.size': 12})
plt.rc('xtick', labelsize = 10)
plt.rc('ytick', labelsize = 10)

fig, axes = plt.subplots(nrows = 1, ncols = 2, figsize=(6.4*2, 4.8))

confusion = conf_matrix(its, vtc, speakers)
sns.heatmap(confusion, annot = True, fmt = '.2f', ax = axes[0], cmap = 'Reds')
axes[0].set_xlabel('its')
axes[0].set_ylabel('vtc')
axes[0].xaxis.set_ticklabels(speakers)
axes[0].yaxis.set_ticklabels(speakers)

confusion = conf_matrix(vtc, its, speakers)
sns.heatmap(confusion, annot = True, fmt = '.2f', ax = axes[1], cmap = 'Reds')
axes[1].set_xlabel('vtc')
axes[1].set_ylabel('its')
axes[1].xaxis.set_ticklabels(speakers)
axes[1].yaxis.set_ticklabels(speakers)

plt.savefig('Fig5.pdf', bbox_inches = 'tight')