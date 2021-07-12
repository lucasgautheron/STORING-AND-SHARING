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
sets = ['its', 'vtc (conf 50%)', 'vtc (drop 50%)', 'vtc (conf 75%)', 'vtc (drop 75%)']

def confusion(segments, prob):
    segments['speaker_type'] = segments['speaker_type'].apply(
        lambda s: random.choice(speakers) if random.random() < prob else s
    )
    return segments

def drop(segments, prob):
    return segments.sample(frac = 1-prob)

if __name__ == '__main__':
    if not os.path.exists('scores.csv'):
        from pyannote.metrics.detection import DetectionPrecisionRecallFMeasure

        path = sys.argv[1]
        project = ChildProject(path)
        am = AnnotationManager(project)
        am.read()

        intersection = AnnotationManager.intersection(am.annotations, ['vtc', 'its'])
        segments = am.get_collapsed_segments(intersection)
        segments = segments[segments['speaker_type'].isin(speakers)]

        conf50 = segments[segments['set'] == 'vtc'].copy()
        conf50 = confusion(conf50, 0.5)
        conf50['set'] = 'vtc (conf 50%)'

        conf75 = segments[segments['set'] == 'vtc'].copy()
        conf75 = confusion(conf75, 0.75)
        conf75['set'] = 'vtc (conf 75%)'

        drop50 = segments[segments['set'] == 'vtc'].copy()
        drop50 = drop(drop50, 0.5)
        drop50['set'] = 'vtc (drop 50%)'

        drop75 = segments[segments['set'] == 'vtc'].copy()
        drop75 = drop(drop75, 0.75)
        drop75['set'] = 'vtc (drop 75%)'

        segments = pd.concat([segments, conf50, conf75, drop50, drop75])

        metric = DetectionPrecisionRecallFMeasure()

        scores = []
        for speaker in speakers:
            ref = segments_to_annotation(segments[(segments['set'] == 'vtc') & (segments['speaker_type'] == speaker)], 'speaker_type')

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
            ax.set_xticklabels(sets, rotation = 45, horizontalalignment = 'right')
        else:
            ax.set_xticklabels(['' for i in range(len(sets))])

        if i%2 == 1:
            ax.set_yticklabels(['' for i in range(6)])

        ax.set_xlabel(speaker)

        _scores = scores[scores['speaker'] == speaker]
        for metric in ['recall', 'precision', 'f']:
            ax.scatter(
                x = _scores['set'].apply(lambda s: sets.index(s)),
                y = _scores[metric],
                label = labels[metric],
                s = 15,
                marker = styles[metric]
            )

    ax = plt.subplot(2, 2, 2)
    ax.legend(loc = "upper right", borderaxespad = 0.1, bbox_to_anchor=(1, 1.25), ncol = 3)

    plt.subplots_adjust(wspace = 0.15)
    plt.savefig('Fig4.pdf', bbox_inches = 'tight')
