#!/usr/bin/env python

"""
Calculating approximate time resolution for Gekko.
"""

import os
import sys
import math
import glob

import pycoevolity
import gekgo_util


def summarize_difference_in_root_heights(
        root_label_1,
        root_label_2):
    log_paths = glob.glob(os.path.join(gekgo_util.ECOEVOLITY_OUTPUT_DIR,
            "run-?-gekko-rate2000-state-run-1.log.gz"))
    assert len(log_paths) == 10
    summary = pycoevolity.stats.SampleSummarizer()
    sample_iter = pycoevolity.parsing.spreadsheet_iter(log_paths, offset = 101)
    ntotal = 0
    nsamples = 0
    for sample in sample_iter:
        ntotal += 1
        i1 = sample["root_height_index_" + root_label_1]
        i2 = sample["root_height_index_" + root_label_2]
        if i1 != i2:
            t1 = float(sample["root_height_" + root_label_1])
            t2 = float(sample["root_height_" + root_label_2])
            summary.add_sample(math.fabs(t1 - t2))
            nsamples += 1
    assert ntotal == 14000
    assert nsamples == summary.n
    return summary


def main():
    # Assuming a rate an order of magnitude faster than estimated for
    # phosducin for Philippine Gekko by Siler et al. 2012
    murate = (1.18e-4 / 1e6) * 10
    interglacial_interval = 5000
    max_interglacial_time_diff = murate * interglacial_interval
    time_diff_summary = summarize_difference_in_root_heights(
            root_label_1 = "Panay13",
            root_label_2 = "Sabtang15"
            )
    sys.stdout.write("Assumed mutation rate:\n")
    sys.stdout.write("{0}\n".format(murate))
    sys.stdout.write(
            "Mean absolute div time difference between\n"
            "\tPanay | Masbate and\n"
            "\tSabtang | Batan:\n")
    sys.stdout.write("{0} (n = {1})\n".format(
            time_diff_summary.mean,
            time_diff_summary.n))
    sys.stdout.write("Maximum div time difference during interglacial:\n")
    sys.stdout.write("{0}\n".format(max_interglacial_time_diff))

if __name__ == '__main__':
    main()
