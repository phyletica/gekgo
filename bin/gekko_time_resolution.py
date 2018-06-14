#!/usr/bin/env python

"""
Calculating approximate time resolution for Gekko.
"""

import os
import sys
import glob

import pycoevolity
import gekgo_util


def get_root_height_means():
    log_paths = glob.glob(os.path.join(gekgo_util.ECOEVOLITY_OUTPUT_DIR,
            "run-?-gekko-rate2000-state-run-1.log.gz"))
    assert len(log_paths) == 10
    sample_iter = pycoevolity.parsing.spreadsheet_iter(log_paths, offset = 101)
    summary = {}
    for sample in sample_iter:
        for key, value in sample.items():
            if key.startswith("root_height") and (
                    not key.startswith("root_height_index")):
                if key in summary:
                    summary[key].add_sample(float(value))
                else:
                    ss = pycoevolity.stats.SampleSummarizer()
                    ss.add_sample(float(value))
                    summary[key] = ss
    assert len(summary) == 8
    for k, s in summary.items():
        assert s.n == 14000
    return summary


def main():
    # Assuming a rate an order of magnitude faster than estimated for
    # phosducin for Philippine Gekko by Siler et al. 2012
    murate = (1.18e-4 / 1e6) * 10
    interglacial_interval = 10000
    max_interglacial_time_diff = murate * 10000
    posterior_root_height_summaries = get_root_height_means()
    min_time_diff = (
            posterior_root_height_summaries["root_height_BabuyanClaro8"].mean -
            posterior_root_height_summaries["root_height_Romblon16"].mean
            )
    sys.stdout.write("Assumed mutation rate:\n")
    sys.stdout.write("{0}\n".format(murate))
    sys.stdout.write(
            "Div time difference between\n"
            "\tBabuyan Claro | Calayan and\n"
            "\tRomblon | Tablas:\n")
    sys.stdout.write("{0}\n".format(min_time_diff))
    sys.stdout.write("Maximum div time difference during interglacial:\n")
    sys.stdout.write("{0}\n".format(max_interglacial_time_diff))

if __name__ == '__main__':
    main()
