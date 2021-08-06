#!/usr/bin/env python3

from ChildProject.projects import ChildProject
from ChildProject.annotations import AnnotationManager
from ChildProject.metrics import segments_to_annotation

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import random
import sys

speakers = ['CHI', 'OCH', 'FEM', 'MAL']

sets = {
    'vtc': 'VTC',
    'its': 'LENA',
    'cha/aligned': 'chat+mfa'
}

if __name__ == '__main__':
    if not os.path.exists('scores.csv'):
        from pyannote.metrics.detection import DetectionPrecisionRecallFMeasure

        path = sys.argv[1]
        project = ChildProject(path)
        am = AnnotationManager(project)
        am.read()

        intersection = AnnotationManager.intersection(am.annotations, ['eaf'] + list(sets.keys()))
        segments = am.get_collapsed_segments(intersection)
        segments = segments[segments['speaker_type'].isin(speakers)]

        metric = DetectionPrecisionRecallFMeasure()

        scores = []
        for speaker in speakers:
            ref = segments_to_annotation(segments[(segments['set'] == 'eaf') & (segments['speaker_type'] == speaker)], 'speaker_type')

            for s in sets:
                hyp = segments_to_annotation(segments[(segments['set'] == s) & (segments['speaker_type'] == speaker)], 'speaker_type')
                detail = metric.compute_components(ref, hyp)
                precision, recall, f = metric.compute_metrics(detail)

                scores.append({
                    'set': s,
                    'speaker': speaker,
                    'recall': recall,
                    'precision': precision,
                    'f': f
                })

        scores = pd.DataFrame(scores)
        scores.to_csv('scores.csv', index = False)

    scores = pd.read_csv('scores.csv')

    plt.rcParams.update({'font.size': 12})
    plt.rc('xtick', labelsize = 10)
    plt.rc('ytick', labelsize = 10)

    print(scores)

    styles = {
        'recall': 's',
        'precision': 'D',
        'f': 'o'
    }

    labels = {
        'recall': 'recall',
        'precision': 'precision',
        'f': 'F-measure'
    }

    plt.figure(figsize = (6.4*1, 4.8*1+0.25*4.8))

    for speaker in speakers:
        i = speakers.index(speaker)
        ax = plt.subplot(2, 2, i+1)
        ax.set_xlim(-0.5,len(sets)-0.5)
        ax.set_ylim(0, 1)

        if i >= 2:
            ax.set_xticks(range(len(sets)))
            ax.set_xticklabels(sets.values(), rotation = 45, horizontalalignment = 'right')
        else:
            ax.set_xticklabels(['' for i in range(len(sets))])

        if i%2 == 1:
            ax.set_yticklabels(['' for i in range(6)])

        ax.set_xlabel(speaker)

        _scores = scores[scores['speaker'] == speaker]
        for metric in ['recall', 'precision', 'f']:
            ax.scatter(
                x = _scores['set'].apply(lambda s: list(sets.keys()).index(s)),
                y = _scores[metric],
                label = labels[metric],
                s = 15,
                marker = styles[metric]
            )

    ax = plt.subplot(2, 2, 2)
    ax.legend(loc = "upper right", borderaxespad = 0.1, bbox_to_anchor=(1, 1.25), ncol = 3)

    plt.subplots_adjust(wspace = 0.15)
    plt.savefig('Fig4.pdf', bbox_inches = 'tight')
