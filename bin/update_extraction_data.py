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

def parse_extractions(file_obj, delimiter='\t', samples=SampleDatabase()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        field_series = line_dict['field_series']
        field_number = line_dict['field_number']
        if line_dict['found'].strip() == "0":
            found = False
        else:
            found = True
        rnase = False
        material = None
        extracted = False
        protocol = None
        preservative = None
        if found:
            rnase = True
            extracted = True
            protocol = 'guanidine thiocyanate'
            material = 'liver'
            if line_dict['material'].strip() != '':
                material = line_dict['material']
            preservative = line_dict['preservative']
        notes = line_dict['notes']
        tube_data = parse_tube_data(line_dict['tube_data'])
        tissue_sample = Tissue(found=found,
                material=material,
                preservative=preservative,
                tube_data=tube_data,
                notes=notes)
        extraction = DnaExtraction(extracted=extracted,
                protocol=protocol,
                rnase=rnase)
        s = Sample(field_series = line_dict['field_series'],
                   field_number = line_dict['field_number'])
        s.tissue_sample = tissue_sample
        s.extraction = extraction
        samples.add(s)
    return samples

def parse_tube_data(string):
    data = {}
    if string.strip() == '':
        return data
    items = string.split(';')
    for i in items:
        kv = i.split(':')
        assert len(kv) == 2, 'problem parsing tube note {0!r}'.format(
                string)
        data[kv[0].strip()] = kv[1].strip()
    return data

def get_samples_with_dna(sample_db):
    dna_samples = SampleDatabase()
    for k, sample in sample_db.iteritems():
        if sample.tissue_sample:
            assert sample.extraction
            new_sample = copy.deepcopy(sample)
            dna_samples.add(new_sample)
    return dna_samples

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
        else:
            tally += 1
    _LOG.info('{0} samples with dna!'.format(tally))
    return 0

def main():
    # inputs
    path_to_extract_data = os.path.join(gekgo_util.LABWORK_DIR,
            "sources",
            "tissue_subsampling.txt")
    # outputs
    dna_data_out_path = os.path.join(gekgo_util.LABWORK_DIR,
            "samples_with_dna.txt")

    # load database
    db = SampleDatabase(path=gekgo_util.DB_PATH)
    # test if script has been run
    for k, sample in db.iteritems():
        if sample.tissue_sample or sample.extraction:
            _LOG.error('Database already has extraction data!\n'
                'I.e., this script has already been successfully used.\n'
                'Write a different script to update info, as this script\n'
                'may be out-of-date and could delete data')
            sys.exit(-1)

    extract_data = parse_extractions(path_to_extract_data)

    for k, sample in extract_data.iteritems():
        db[k].tissue_sample = sample.tissue_sample
        db[k].extraction = sample.extraction

    rc = check_database(db)
    if rc == 0:
        db.commit()

    dna_samples = get_samples_with_dna(db)
    # import code; code.interact(local=locals());
    dna_samples.write_flat_file(
            path=dna_data_out_path)

if __name__ == '__main__':
    main()
