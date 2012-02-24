#! /usr/bin/env python

import os
import sys
import logging
import glob
import stat

BIN_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.dirname(BIN_DIR))
DATA_DIR = os.path.abspath(os.path.join(PROJECT_DIR, 'data'))
LOCI_DIR = os.path.abspath(os.path.join(DATA_DIR, 'loci'))
CONCAT_DIR = os.path.abspath(os.path.join(DATA_DIR, 'concat'))
LOCI = [os.path.basename(os.path.dirname(x)) for x in glob.glob(
        os.path.join(LOCI_DIR, "*/"))]
LOCI_ALNS_FASTA = {}
LOCI_ALNS_PHY = {}
LOCI_ALNS_NEX = {}
for i in LOCI:
    x = glob.glob(os.path.join(LOCI_DIR, i, 'aln', 'final', '*.fasta'))
    assert(len(x) == 1)
    LOCI_ALNS_FASTA[i] = x[0]
    x = glob.glob(os.path.join(LOCI_DIR, i, 'aln', 'final', '*.phy'))
    assert(len(x) == 1)
    LOCI_ALNS_PHY[i] = x[0]
    x = glob.glob(os.path.join(LOCI_DIR, i, 'aln', 'final', '*.nex'))
    assert(len(x) == 1)
    LOCI_ALNS_NEX[i] = x[0]
CONCAT_ALNS_NEX = {'all': os.path.join(CONCAT_DIR, 'all.nex'),
                   'nuc': os.path.join(CONCAT_DIR, 'nuc.nex')}

def whereis(file_name):
    """
    Returns the first absolute path to `file_name` encountered in $PATH.
    Returns `None` if `file_name` is not found in $PATH.
    """
    paths = os.environ.get('PATH', '').split(':')
    for path in paths:
        abs_path = os.path.join(path, file_name)
        if os.path.exists(abs_path) and not os.path.isdir(abs_path):
            return abs_path
            break
    return None

def mkdr(path):
    """
    Creates directory `path`, but suppresses error if `path` already exists.
    """
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

def is_file(path):
    if not path:
        return False
    if not os.path.isfile(path):
        return False
    return True

def is_executable(path):
    is_f = is_file(path)
    if not is_f:
        return False
    if (os.stat(path)[stat.ST_MODE] & (stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH)) == 0:
        return False
    return True

def get_qsub_preamble(memory = "2G", queue = "general.q"):
    return """#! /bin/sh
#$ -S /bin/bash
#$ -cwd
#$ -V
#$ -l h_vmem=%s
#$ -l vf=%s
#$ -q %s

source ~/.bash_profile
cd /share/work1
cd $SGE_O_WORKDIR
""" % (memory, memory, queue)

class RunLogger(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "RunLog")
        self._log = logging.getLogger(self.name)
        self._log.setLevel(logging.DEBUG)
        if kwargs.get("log_to_stderr", True):
            ch1 = logging.StreamHandler()
            ch1.setLevel(self.get_logging_level(
                    kwargs.get("stderr_level", logging.INFO)))
            ch1.setFormatter(
                    self.get_logging_formatter(
                            kwargs.get("stderr_format", None)))
            self._log.addHandler(ch1)
        if kwargs.get("log_to_file", True):
            log_stream = kwargs.get(
                    "log_stream",
                    open(kwargs.get("log_path", self.name + ".log"), "w"))
            ch2 = logging.StreamHandler(log_stream)
            ch2.setLevel(self.get_logging_level(
                    kwargs.get("file_level", logging.INFO)))
            ch2.setFormatter(
                    self.get_logging_formatter(
                            kwargs.get("file_format", None)))
            self._log.addHandler(ch2)

    def get_logging_level(self, level=None):
        if level in [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING,
            logging.ERROR, logging.CRITICAL]:
            return level
        elif level is not None:
            level_name = str(level).upper()
        elif '_LOGGING_LEVEL_ENVAR' in os.environ:
            level_name = os.environ['_LOGGING_LEVEL_ENVAR'].upper()
        else:
            level_name = "NOTSET"
        if level_name == "NOTSET":
            return logging.NOTSET
        elif level_name == "DEBUG":
            return logging.DEBUG
        elif level_name == "INFO":
            return logging.INFO
        elif level_name == "WARNING":
            return logging.WARNING
        elif level_name == "ERROR":
            return logging.ERROR
        elif level_name == "CRITICAL":
            return logging.CRITICAL
        else:
            return logging.NOTSET

    def get_default_formatter(self):
        f = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        f.datefmt='%Y-%m-%d %H:%M:%S'
        return f

    def get_rich_formatter(self):
        f = logging.Formatter("[%(asctime)s] %(filename)s (%(lineno)d): %(levelname) 8s: %(message)s")
        f.datefmt='%Y-%m-%d %H:%M:%S'
        return f

    def get_simple_formatter(self):
        return logging.Formatter("%(levelname) 8s: %(message)s")

    def get_raw_formatter(self):
        return logging.Formatter("%(message)s")

    def get_logging_formatter(self, format=None):
        if format is not None:
            format = format.upper()
        elif '_LOGGING_FORMAT_ENVAR' in os.environ:
            format = os.environ['_LOGGING_FORMAT_ENVAR'].upper()
        if format == "RICH":
            return self.get_rich_formatter()
        elif format == "SIMPLE":
            return self.get_simple_formatter()
        elif format == "NONE":
            return self.get_raw_formatter()
        else:
            return self.get_default_formatter()
 
    def debug(self, msg, *args, **kwargs):
        self._log.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log.critical(msg, *args, **kwargs)

def main():
    sys.stdout.write("%s" % PROJECT_DIR)

if __name__ == '__main__':
    main()

