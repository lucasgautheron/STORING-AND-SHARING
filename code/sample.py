#!/usr/bin/env python3

from ChildProject.projects import ChildProject
from ChildProject.annotations import AnnotationManager

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
import numpy as np
import os
import pandas as pd
import librosa

if __name__ == "__main__":
    project = ChildProject("vandam-data")

    am = AnnotationManager(project)
    am.read()

    annotations = AnnotationManager.intersection(
        am.annotations, ["its", "cha", "eaf"]
    )

    annotations["converted_filename"] = annotations["recording_filename"].apply(
        lambda f: project.get_converted_recording_filename("standard", f)
    )

    annotations = annotations[
        annotations["range_onset"] == annotations["range_onset"].iloc[-1]
    ]
    annotations['range_onset'] += 20000
    annotations["range_offset"] = annotations["range_onset"] + 5000

    range_onset = annotations["range_onset"].iloc[0]
    range_offset = annotations["range_offset"].iloc[0]

    signal, sr = librosa.load(
        os.path.join(
            project.path,
            "recordings/converted/standard",
            annotations["converted_filename"].iloc[0],
        ),
        sr=8000,
        offset=range_onset / 1000,
        duration=(range_offset - range_onset) / 1000,
    )

    time = np.arange(
        range_onset / 1000,
        range_offset / 1000,
        1 / sr,
    )

    plt.plot(time, .5*signal, color = 'black')

    positions = {"eaf": -0.4, "cha": -0.6, "its": -0.8}
    annotators = {"its": '\\textbf{LENA}', 'cha': '\\textbf{Annotator 2}\n\\textbf{(CHAT)}', 'eaf': '\\textbf{Annotator 1}\n\\textbf{(ELAN)}'}
    colors = {"MAL": "red", "FEM": "blue", "CHI": "green"}
    speakers = {"MAL": "male adult", "FEM": "female adult", "CHI": "key child"}
    ids = {'MA1': 'Father', 'FA1': 'Mother'}

    segments = am.get_segments(annotations)

    for segment in segments.to_dict(orient="records"):
        speaker_type = segment["speaker_type"]

        if speaker_type not in ["MAL", "FEM", "CHI"]:
            continue

        t1 = segment["segment_onset"] / 1000
        t2 = segment["segment_offset"] / 1000
        y = positions[segment["set"]]

        plt.plot([t1, t2], [y, y], color=colors[speaker_type], marker = "|")

        if segment["set"] == "cha":
            transcription = segment['transcription']
            if len(transcription) > 20:
                transcription = transcription[:20] + '...'

            text = f"``{transcription}''"
        elif segment["set"] == "its":
            text = '{}, {} words'.format(
                speakers[speaker_type], int(segment["words"])
            )
        else:
            text = '{}'.format(ids[segment['speaker_id']])

        plt.text(t1, y + 0.05, text)

    plt.text(range_onset/1000-0.8, 0, '\\textbf{Audio}', ha = 'center')

    for set in positions:
        y = positions[set]
        plt.text(range_onset/1000-0.8, y, annotators[set], ha = 'center')


    plt.axis("off")
    plt.savefig("Fig2.pdf", bbox_inches = 'tight')
