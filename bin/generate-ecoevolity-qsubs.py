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

import gekgo_util

_RNG = random.Random()

def get_pbs_header(walltime = "5:00:00"):
    s = ("#! /bin/sh\n"
         "#PBS -l nodes=1:ppn=1\n"
         "#PBS -l walltime={0}\n"
         "#PBS -j oe\n".format(walltime))
    s += ("\n"
          "if [ -n \"$PBS_JOBNAME\" ]\n"
          "then\n"
          "    source \"${PBS_O_HOME}/.bash_profile\"\n"
          "    cd \"$PBS_O_WORKDIR\"\n"
          "    module load gcc/5.3.0\n"
          "fi\n\n")
    return s

def write_qsub(config_path,
        run_number = 1,
        walltime = "2:00:00",
        rng = _RNG):
    config_name = os.path.basename(config_path)
    config_prefix = os.path.splitext(config_name)[0]
    qsub_path = os.path.join(
            gekgo_util.ECOEVOLITY_QSUB_DIR,
            "{0}-run-{1}.sh".format(config_prefix, run_number))
    no_data_qsub_path = os.path.join(
            gekgo_util.ECOEVOLITY_QSUB_DIR,
            "no-data-{0}-run-{1}.sh".format(config_prefix, run_number))
    seed = rng.randint(1, 999999999)
    prefix_dir = os.path.relpath(gekgo_util.ECOEVOLITY_OUTPUT_DIR,
            gekgo_util.ECOEVOLITY_QSUB_DIR)
    prefix = os.path.join(prefix_dir, "run-{0}".format(run_number))
    no_data_prefix = os.path.join(prefix_dir,
            "no-data-run-{0}".format(run_number))
    stdout_path = prefix + "-" + config_prefix + ".out"
    no_data_stdout_path = no_data_prefix + "-" + config_prefix + ".out"
    if not os.path.exists(qsub_path):
        with open(qsub_path, 'w') as out:
            out.write(get_pbs_header(walltime))
            out.write("prefix={0}\n\n".format(prefix))
            out.write(
                    "ecoevolity --seed {seed} --prefix {prefix} "
                    "--relax-missing-sites "
                    "--relax-constant-sites "
                    "--relax-triallelic-sites "
                    "{config_path} 1>{stdout_path} 2>&1\n".format(
                    seed = seed,
                    prefix = prefix,
                    config_path = config_path,
                    stdout_path = stdout_path))
    if not os.path.exists(no_data_qsub_path):
        with open(no_data_qsub_path, 'w') as out:
            out.write(get_pbs_header(walltime))
            out.write("prefix={0}\n\n".format(no_data_prefix))
            out.write(
                    "ecoevolity --seed {seed} --prefix {prefix} "
                    "--ignore-data "
                    "--relax-missing-sites "
                    "--relax-constant-sites "
                    "--relax-triallelic-sites "
                    "{config_path} 1>{stdout_path} 2>&1\n".format(
                    seed = seed,
                    prefix = no_data_prefix,
                    config_path = config_path,
                    stdout_path = no_data_stdout_path))

def arg_is_positive_int(i):
    """
    Returns int if argument is a positive integer; returns argparse error
    otherwise.

    >>> arg_is_positive_int(1) == 1
    True
    """

    try:
        if int(i) < 1:
            raise
    except:
        msg = '{0!r} is not a positive integer'.format(i)
        raise argparse.ArgumentTypeError(msg)
    return int(i)


def main_cli(argv = sys.argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--number-of-runs',
            action = 'store',
            type = int,
            default = 10,
            help = 'Number of qsubs to generate per config (Default: 5).')
    parser.add_argument('--walltime',
            action = 'store',
            type = str,
            default = '20:00:00',
            help = 'Walltime for qsub scripts (Default: 5:00:00).')

    if argv == sys.argv:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)
    _RNG.seed(8162014)

    if not os.path.exists(gekgo_util.ECOEVOLITY_OUTPUT_DIR):
        os.mkdir(gekgo_util.ECOEVOLITY_OUTPUT_DIR)
    if not os.path.exists(gekgo_util.ECOEVOLITY_QSUB_DIR):
        os.mkdir(gekgo_util.ECOEVOLITY_QSUB_DIR)

    config_path_pattern = os.path.join(gekgo_util.ECOEVOLITY_CONFIG_DIR,
            "*.yml") 
    for config_path in glob.glob(config_path_pattern):
        rel_config_path = os.path.relpath(config_path,
                gekgo_util.ECOEVOLITY_QSUB_DIR)
        for i in range(args.number_of_runs):
            write_qsub(
                    config_path = rel_config_path,
                    run_number = i + 1,
                    walltime = args.walltime)


if __name__ == "__main__":
    main_cli()
