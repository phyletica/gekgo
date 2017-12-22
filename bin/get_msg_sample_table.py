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
                    'catalog_series', 
                    'catalog_number',
                    'field_series',
                    'field_number',
                    'genus',
                    'epithet',
                    'country',
                    'island',
                    # 'paic',
                    'locality',
                    'lat',
                    'long',
                    'date',
                    # 'tissue',
                    # 'tissue_sample.found',
                    # 'tissue_sample.material',
                    # 'tissue_sample.preservative',
                    # 'tissue_sample.tube_data',
                    # 'tissue_sample.notes',
                    # 'extraction.protocol',
                    # 'extraction.rnase',
                    # 'extraction.qubit',
                    # 'extraction.notes',
                    # 'extraction.gel_lane',
                    # 'extraction.plate',
                    # 'extraction.row',
                    # 'extraction.column',
                    'extraction.msg_barcode',
                    # 'extraction.dilution',
                    # 'cam_extract',
                    # 'cam_extract_cell',
                    # 'source',
                    ],
            header = True,
            keys = sorted(msg_samples.keys()))

    
if __name__ == '__main__':
    main()
