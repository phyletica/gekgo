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

def parse_data(lane_qubit_file,
               plate_well_file,
               delimiter='\t'):
    qubit_samples = parse_lane_qubit_data(lane_qubit_file, delimiter=delimiter)
    well_samples = parse_well_data(plate_well_file, delimiter=delimiter)
    for k, sample in well_samples.iteritems():
        assert k in qubit_samples.keys()
        assert sample.extraction.qubit == qubit_samples[k].extraction.qubit
        assert qubit_samples[k].extraction.plate == None
        assert sample.extraction.plate != None
        assert qubit_samples[k].extraction.row == None
        assert sample.extraction.row != None
        assert qubit_samples[k].extraction.column == None
        assert sample.extraction.column != None
        assert qubit_samples[k].extraction.dilution == None
        assert sample.extraction.dilution != None
        qubit_samples[k].extraction.plate = sample.extraction.plate
        qubit_samples[k].extraction.row = sample.extraction.row
        qubit_samples[k].extraction.column = sample.extraction.column
        qubit_samples[k].extraction.dilution = sample.extraction.dilution
    return qubit_samples

def parse_lane_qubit_data(file_obj, delimiter='\t', samples=SampleDatabase()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        field_series = line_dict['field_series'].strip()
        field_number = line_dict['field_number'].strip()
        qubit = line_dict['qubit'].strip()
        if qubit == '' or qubit == None:
            qubit = None
        else:
            qubit = float(qubit)
        lane = line_dict['lane'].strip()
        if lane == '' or lane == None:
            raise Exception('problem parsing lane data from row {0}'.format(
                    n))
        extraction = DnaExtraction(
                qubit = qubit,
                gel_lane = int(lane))
        s = Sample(field_series = line_dict['field_series'],
                   field_number = line_dict['field_number'])
        s.extraction = extraction
        samples.add(s)
    return samples

def parse_well_data(file_obj, delimiter='\t', samples=SampleDatabase()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        field_series = line_dict['field_series'].strip()
        field_number = line_dict['field_number'].strip()
        plate = line_dict['plate'].strip()
        col = line_dict['col'].strip().upper()
        row = line_dict['row'].strip()
        qubit = line_dict['qubit'].strip()
        if not plate in ['1', '2', '3']:
            raise Exception('unexpected plate value {0} at row {1}'.format(
                    plate, n))
        if not row in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            raise Exception('unexpected row value {0} at row {1}'.format(
                    row, n))
        if not col in [str(x) for x in range(1, 13)]:
            raise Exception('unexpected col value {0} at col {1}'.format(
                    col, n))
        if qubit == '' or qubit == None:
            raise Exception('could not parse qubit value at row {0}'.format(n))
        extraction = DnaExtraction(
                qubit = float(qubit),
                plate = int(plate),
                column = int(col),
                row = row.upper(),
                dilution = 5.0)
        s = Sample(field_series = line_dict['field_series'],
                   field_number = line_dict['field_number'])
        s.extraction = extraction
        samples.add(s)
    return samples

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
        if not sample.tissue_sample:
            assert not sample.extraction
            assert sample.tissue_sample.found == False
            assert sample.extraction.extracted == False
            assert sample.tissue_sample.material == None
            assert sample.tissue_sample.preservative == None, ('{0}: {1!r}'.format(
                    sample.field_id, sample.tissue_sample.preservative))
            assert sample.tissue_sample.tube_data == {}
            assert sample.extraction.protocol == None
            assert sample.extraction.notes == None
            assert sample.extraction.rnase == False
            assert sample.extraction.gel_lane == None
            assert sample.extraction.plate == None, 'plate was {0!r} for {1}'.format(
                    sample.extraction.plate, k)
            assert sample.extraction.row == None
            assert sample.extraction.column == None
            assert sample.extraction.dilution == None
        else:
            tally += 1
    _LOG.info('{0} samples with dna!'.format(tally))
    return 0

def main():
    # inputs
    path_to_qubit_data = os.path.join(gekgo_util.LABWORK_DIR,
            "sources",
            "gel_lane_and_qubit.txt")
    path_to_well_data = os.path.join(gekgo_util.LABWORK_DIR,
            "sources",
            "plate_well_info.txt")
    # outputs
    plate_data_out_path = os.path.join(gekgo_util.LABWORK_DIR,
            "msg_library_samples.txt")
    dna_data_out_path = os.path.join(gekgo_util.LABWORK_DIR,
            "samples_with_dna.txt")

    # load database
    db = SampleDatabase(path=gekgo_util.DB_PATH)
    # test if script has been run
    for k, sample in db.iteritems():
        if sample.extraction.gel_lane != None or \
           sample.extraction.plate != None or \
           sample.extraction.row != None or \
           sample.extraction.column != None or \
           sample.extraction.dilution != None:
            _LOG.error('Database already has concentration and plate data!\n'
                'I.e., this script has already been successfully used.\n'
                'Write a different script to update info, as this script\n'
                'may be out-of-date and could delete data')
            sys.exit(-1)

    new_extraction_data = parse_data(
            lane_qubit_file = path_to_qubit_data,
            plate_well_file = path_to_well_data)

    for k, sample in new_extraction_data.iteritems():
        assert k in db.keys()
        db[k].extraction.gel_lane = sample.extraction.gel_lane
        db[k].extraction.qubit = sample.extraction.qubit
        db[k].extraction.plate = sample.extraction.plate
        db[k].extraction.row = sample.extraction.row
        db[k].extraction.column = sample.extraction.column
        db[k].extraction.dilution = sample.extraction.dilution
        if k == 'KU-FS 16':
            db[k].tissue_sample.found = True
            db[k].tissue_sample.material = 'liver'
            db[k].tissue_sample.preservative = 'frozen'
            db[k].extraction.extracted = True
            db[k].extraction.protocol = 'guanidine thiocyanate'
            db[k].extraction.rnase = True

    rc = check_database(db)
    if rc == 0:
        db.commit()

    library_samples = get_samples_for_libraries(db)
    # import code; code.interact(local=locals());
    library_samples.write_flat_file(
            path=plate_data_out_path)

    dna_samples = get_samples_with_dna(db)
    dna_samples.write_flat_file(
            path=dna_data_out_path)

if __name__ == '__main__':
    main()

