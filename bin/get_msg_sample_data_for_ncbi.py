#! /usr/bin/env python

import os
import sys
import logging
import copy

import gekgo_util
from data_classes import Sample, SampleDatabase, Tissue, DnaExtraction

_LOG = gekgo_util.RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

def get_msg_samples(sample_db):
    samples = SampleDatabase()
    for k, sample in sample_db.iteritems():
        if sample.extraction.plate != None:
            new_sample = copy.deepcopy(sample)
            samples.add(new_sample)
    return samples

def main():
    # load database
    db = SampleDatabase(path=gekgo_util.DB_PATH)
    msg_samples = get_msg_samples(db)
    msg_samples.write_flat_file_to_stream(
            stream = sys.stdout,
            delimiter = '\t',
            fields = [
                    'catalog_id',
                    'seq_label',
                    'long_seq_label',
                    'species',
                    'lat_long',
                    'catalog_series', 
                    'catalog_number',
                    'field_series',
                    'field_number',
                    'genus',
                    'epithet',
                    'country',
                    'island',
                    'locality',
                    'lat',
                    'long',
                    'date',
                    'tissue_sample.material',
                    'tissue_sample.preservative',
                    'extraction.protocol',
                    'extraction.rnase',
                    'extraction.msg_barcode',
                    ],
            header = True,
            keys = sorted(msg_samples.keys()))

    
if __name__ == '__main__':
    main()
