#! /usr/bin/env python

"""
Calculate the posterior probability that the Gekko pairs Panay-Masbate and
Sabtang-Batan co-diverged.
"""

import os
import sys
import glob
import logging

import gekgo_util

import pycoevolity

_LOG = gekgo_util.RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

def main():
    paths = glob.glob(os.path.join(gekgo_util.ECOEVOLITY_OUTPUT_DIR,
            "run-?-gekko-rate2000-state-run-1.log"))
    posterior = pycoevolity.posterior.PosteriorSummary(paths, burnin = 101)
    post_prob_shared = 0.0
    sys.stdout.write("model\tpost_prob\n")
    for model, prob in posterior.get_models():
        sys.stdout.write("{model}\t{post_prob}\n".format(
                model = model,
                post_prob = prob))
        if model[3] == model[5]:
            post_prob_shared += prob
    sys.stdout.write("{0}\n".format(post_prob_shared))


if __name__ == '__main__':
    main()
