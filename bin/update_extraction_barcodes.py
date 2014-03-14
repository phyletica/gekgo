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
from update_extraction_data import get_samples_with_dna

_LOG = RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

def parse_barcodes(barcode_data_file, delimiter = '\t'):
    barcodes = {}
    dr, src = get_dict_reader(barcode_data_file, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        well1 = line_dict['ID1'].strip().split('_')[0].upper()
        well2 = line_dict['ID2'].strip().split('_')[0].upper()
        assert well1 == well2
        barcode = line_dict['Barcode'].strip().upper()
        barcodes[well1] = barcode
    assert len(barcodes) == 96
    return barcodes

def get_samples_for_libraries(sample_db):
    samples = SampleDatabase()
    for k, sample in sample_db.iteritems():
        if sample.extraction.plate != None:
            new_sample = copy.deepcopy(sample)
            samples.add(new_sample)
    return samples

def check_database(db):
    tally = 0
    for k, sample in db.iteritems():
        if ((sample.extraction.row == None) and
                (sample.extraction.msg_barcode != None)):
            tally += 1
            _LOG.info('sample {0.field_id} in extraction plate, but no '
                    'barcode!'.format(sample))
        if ((sample.extraction.row != None) and
                (sample.extraction.msg_barcode == None)):
            tally += 1
            _LOG.info('sample {0.field_id} not in extraction plate, but has '
                    'barcode!'.format(sample))
    return tally

def write_barcode_maps(db, out_dir):
    file_streams = {}
    for k, sample in db.iteritems():
        if not file_streams.has_key(sample.extraction.plate):
            p = os.path.join(out_dir, 'plate{0}-barcode-map.txt'.format(
                    sample.extraction.plate))
            fs = open(p, 'w')
            file_streams[sample.extraction.plate] = fs
        file_streams[sample.extraction.plate].write('{0}\t{1}\n'.format(
                k, sample.extraction.msg_barcode))
    for k, v in file_streams.iteritems():
        v.close()

def main():
    # inputs
    path_to_barcode_data = os.path.join(gekgo_util.LABWORK_DIR,
            "sources",
            "msg_barcodes.txt")
    # outputs
    plate_data_out_path = os.path.join(gekgo_util.LABWORK_DIR,
            "msg_library_samples.txt")
    dna_data_out_path = os.path.join(gekgo_util.LABWORK_DIR,
            "samples_with_dna.txt")

    barcode_map_dir = os.path.join(gekgo_util.LABWORK_DIR,
            "msg_barcode_maps")
    if not os.path.exists(barcode_map_dir):
        os.mkdir(barcode_map_dir)

    # load database
    db = SampleDatabase(path=gekgo_util.DB_PATH)

    # test if script has been run
    for k, sample in db.iteritems():
        if sample.extraction.msg_barcode != None:
            _LOG.error('Database already has msg barcode data!\n'
                'I.e., this script has already been successfully used.\n'
                'Write a different script to update info, as this script\n'
                'may be out-of-date and could delete data')
            sys.exit(-1)

    barcodes = parse_barcodes(barcode_data_file = path_to_barcode_data)

    for k, sample in db.iteritems():
        sample.extraction.msg_barcode = barcodes.get(
                '{0.row}{0.column}'.format(sample.extraction),
                None)

    rc = check_database(db)
    if rc == 0:
        db.commit()

    library_samples = get_samples_for_libraries(db)
    # import code; code.interact(local=locals());
    library_samples.write_flat_file(
            path=plate_data_out_path)
    write_barcode_maps(library_samples, barcode_map_dir)

    dna_samples = get_samples_with_dna(db)
    dna_samples.write_flat_file(
            path=dna_data_out_path)

if __name__ == '__main__':
    main()

