#! /usr/bin/env python

import sys
import os
import argparse
import random
import glob
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

sys.path.append("../")
import gekgo_util

_RNG = random.Random()

def get_pbs_header():
    s = ("#! /bin/sh\n"
         "\n"
         "if [ -n \"$PBS_JOBNAME\" ]\n"
         "then\n"
         "    cd \"$PBS_O_WORKDIR\"\n"
         "    module load gcc/5.3.0\n"
         "fi\n\n")
    return s

def get_asc_header():
    s = ("#! /bin/sh\n\n"
         "username=\"$USER\"\n"
         "if [ \"$username\" == \"aubjro\" ]\n"
         "then\n"
         "    module load gcc/6.1.0\n"
         "fi\n\n")
    return s

def write_qsub(config_path,
        run_number = 1,
        asc = False,
        relax_missing_sites = False,
        rng = _RNG):
    qsub_prefix = os.path.splitext(config_path)[0]
    qsub_path = "{0}-run-{1}-qsub.sh".format(qsub_prefix, run_number)
    if os.path.exists(qsub_path):
        return
    config_file = os.path.basename(config_path)
    stdout_path = "run-{0}-{1}.out".format(run_number, config_file)
    seed = rng.randint(1, 999999999)
    assert(not os.path.exists(qsub_path))
    with open(qsub_path, 'w') as out:
        if asc:
            out.write(get_asc_header())
        else:
            out.write(get_pbs_header())
        if relax_missing_sites:
            out.write("ecoevolity --seed {0} --prefix run-{1}- --relax-constant-sites --relax-missing-sites {2} 1>{3} 2>&1\n".format(
                    seed,
                    run_number,
                    config_file,
                    stdout_path))
        else:
            out.write("ecoevolity --seed {0} --prefix run-{1}- --relax-constant-sites {2} 1>{3} 2>&1\n".format(
                    seed,
                    run_number,
                    config_file,
                    stdout_path))


def main_cli(argv = sys.argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--seed',
            action = 'store',
            type = int,
            help = 'Random number seed to use for the analysis.')
    parser.add_argument('--number-of-runs',
            action = 'store',
            type = int,
            default = 4,
            help = 'Number of qsubs to generate per config (Default: 4).')
    parser.add_argument('--relax-missing-sites',
            action = 'store_true',
            help = 'Add relax-missing-sites option to scripts. Default: False')
    parser.add_argument('--asc',
            action = 'store_true',
            help = 'Format script for AL super computer.')

    if argv == sys.argv:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)
    if not args.seed:
        args.seed = random.randint(1, 999999999)
    _RNG.seed(args.seed)

    config_path_pattern = os.path.join(gekgo_util.ECOEVOLITY_SIM_DIR, "*", "batch*", "*simcoevolity-sim-*.yml") 
    for config_path in glob.glob(config_path_pattern):
        for i in range(args.number_of_runs):
            write_qsub(config_path = config_path,
                    run_number = i + 1,
                    asc = args.asc,
                    relax_missing_sites = args.relax_missing_sites)
    

if __name__ == "__main__":
    main_cli()
