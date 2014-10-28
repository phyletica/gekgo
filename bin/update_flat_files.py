#! /usr/bin/env python

import os
import sys
import logging
import re
import csv
import itertools
import copy

import gekgo_util
from gekgo_util import RunLogger, get_dict_reader
from data_classes import Sample, SampleDatabase, Tissue, DnaExtraction

_LOG = RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

def get_samples_with_dna(sample_db):
    dna_samples = SampleDatabase()
    for k, sample in sample_db.iteritems():
        if sample.tissue_sample:
            assert sample.extraction, '{0} not extracted'.format(k)
            new_sample = copy.deepcopy(sample)
            dna_samples.add(new_sample)
    return dna_samples

def main():
    # outputs
    flat_db_out_path = os.path.join(gekgo_util.DB_DIR, "flat_data.txt")
    dna_data_out_path = os.path.join(gekgo_util.LABWORK_DIR,
            "samples_with_dna.txt")

    # load database
    db = SampleDatabase(path=gekgo_util.DB_PATH)
    db.write_flat_file(path=flat_db_out_path)

    dna_samples = get_samples_with_dna(db)
    dna_samples.write_flat_file(
            path=dna_data_out_path)

if __name__ == '__main__':
    main()
