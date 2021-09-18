#!/usr/bin/env python3

from ChildProject.projects import ChildProject
from ChildProject.annotations import AnnotationManager
from ChildProject.metrics import segments_to_grid, conf_matrix

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import normalize

import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    "font.serif" : "Times New Roman",
    'text.usetex': True,
    'pgf.rcfonts': False,
})
import sys

speakers = ['CHI', 'OCH', 'FEM', 'MAL']

path = sys.argv[1]

if __name__ == '__main__':
    project = ChildProject(path)
    am = AnnotationManager(project)
    am.read()

    intersection = AnnotationManager.intersection(am.annotations, ['vtc', 'eaf'])
    segments = am.get_collapsed_segments(intersection)
    segments = segments[segments['speaker_type'].isin(speakers)]

    vtc = segments_to_grid(segments[segments['set'] == 'vtc'], 0, segments['segment_offset'].max(), 100, 'speaker_type', speakers)
    eaf = segments_to_grid(segments[segments['set'] == 'eaf'], 0, segments['segment_offset'].max(), 100, 'speaker_type', speakers)

    speakers.extend(['none'])

    confusion_counts = conf_matrix(vtc, eaf)

    plt.rcParams.update({'font.size': 12})
    plt.rc('xtick', labelsize = 10)
    plt.rc('ytick', labelsize = 10)

    fig, axes = plt.subplots(nrows = 1, ncols = 2, figsize=(6.4*2, 4.8))

    confusion = confusion_counts/np.sum(vtc, axis = 0)[:,None]

    sns.heatmap(confusion, annot = True, fmt = '.2f', ax = axes[0], cmap = 'Reds')
    axes[0].set_xlabel('eaf')
    axes[0].set_ylabel('vtc')
    axes[0].xaxis.set_ticklabels(speakers)
    axes[0].yaxis.set_ticklabels(speakers)

    confusion_counts = np.transpose(confusion_counts)
    confusion = confusion_counts/np.sum(eaf, axis = 0)[:,None]

    sns.heatmap(confusion, annot = True, fmt = '.2f', ax = axes[1], cmap = 'Reds')
    axes[1].set_xlabel('vtc')
    axes[1].set_ylabel('eaf')
    axes[1].xaxis.set_ticklabels(speakers)
    axes[1].yaxis.set_ticklabels(speakers)

    plt.savefig('Fig7.pdf', bbox_inches = 'tight')