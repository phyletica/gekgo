#! /usr/bin/env python

import sys
import os
import re
import math
import glob

import pycoevolity
import gekgo_util


def get_worst_values(convergence_table_paths, burnin = 200):
    max_psrf = float('-inf')
    min_ess = float('inf')
    for d in pycoevolity.parsing.spreadsheet_iter(
            convergence_table_paths):
        if int(d["burnin"]) == burnin:
            if float(d["psrf"]) > max_psrf:
                max_psrf = float(d["psrf"])
            if float(d["ess_concat"]) < min_ess:
                min_ess = float(d["ess_concat"])
                sys.stderr.write("{0}\n".format(min_ess))
    return max_psrf, min_ess


def main_cli(argv = sys.argv):

    sys.stdout.write("Summarizing analyses with data...\n")
    convergence_table_paths = glob.glob(os.path.join(
            gekgo_util.ECOEVOLITY_OUTPUT_DIR,
            "pyco-sumchains-*-table.txt"))
    max_psrf, min_ess = get_worst_values(
            convergence_table_paths,
            burnin = 200)
    sys.stdout.write("Max PSRF: {0}\n".format(max_psrf))
    sys.stdout.write("Min ESS: {0}\n".format(min_ess))

    sys.stdout.write("\nSummarizing analyses with no data...\n")
    convergence_table_paths = glob.glob(os.path.join(
            gekgo_util.ECOEVOLITY_OUTPUT_DIR,
            "no-data-pyco-sumchains-*-table.txt"))
    max_psrf, min_ess = get_worst_values(
            convergence_table_paths,
            burnin = 200)
    sys.stdout.write("Max PSRF: {0}\n".format(max_psrf))
    sys.stdout.write("Min ESS: {0}\n".format(min_ess))


if __name__ == "__main__":
    main_cli()
