#! /usr/bin/env python

import os
import sys
import logging
import re
import copy
import argparse

import gekgo_util
from data_classes import Sample, SampleDatabase, Tissue, DnaExtraction

_LOG = gekgo_util.RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

begin_taxa_pattern = re.compile(r"^\s*begin\s+taxa\s*;\s*$", re.IGNORECASE)
taxa_dimensions_pattern = re.compile(
        r"^\s*dimensions\s+ntax\s*=\s*(?P<ntax>\d+)\s*;\s*$",
        re.IGNORECASE)
begin_taxlabels_pattern = re.compile(r"^\s*taxlabels\s*$", re.IGNORECASE)
end_taxlabels_pattern = re.compile(r"^\s*;\s*$")
end_taxa_pattern = re.compile(r"^\s*end;\s*$", re.IGNORECASE)

def parse_seq_labels(nexus_path):
    seq_labels = []
    with open(nexus_path, 'r') as stream:
        for line1 in stream:
            if begin_taxa_pattern.match(line1):
                for line2 in stream:
                    m = taxa_dimensions_pattern.match(line2)
                    if m:
                        ntax = int(m.group("ntax"))
                        for line3 in stream:
                            if begin_taxlabels_pattern.match(line3):
                                for line4 in stream:
                                    if end_taxlabels_pattern.match(line4):
                                        assert ntax == len(seq_labels)
                                        return seq_labels
                                    if line4.strip() == "":
                                        continue
                                    label_elements = line4.strip().split('_')
                                    label = "{0} {1}".format(*label_elements)
                                    seq_labels.append(label)
    assert ntax == len(seq_labels)
    return seq_labels

def get_seq_labels(nexus_paths):
    seq_labels = []
    for path in nexus_paths:
        seq_labels.extend(parse_seq_labels(path))
    return seq_labels

def get_samples_by_label(sample_db, seq_labels):
    samples = SampleDatabase()
    for k, sample in sample_db.items():
        if k in seq_labels:
            new_sample = copy.deepcopy(sample)
            samples.add(new_sample)
    return samples

def get_samples_from_nexus_files(sample_db, nexus_paths):
    seq_labels = get_seq_labels(nexus_paths)
    samples = get_samples_by_label(sample_db, seq_labels)
    return samples, seq_labels

def get_msg_samples(sample_db):
    samples = SampleDatabase()
    for k, sample in sample_db.iteritems():
        if sample.extraction.plate != None:
            new_sample = copy.deepcopy(sample)
            samples.add(new_sample)
    return samples

def get_ecoevolity_alignment_paths():
    paths = []
    for file_name in os.listdir(gekgo_util.ECOEVOLITY_ALIGNMENT_DIR):
        if ((file_name.endswith(".nex")) and (
                not file_name.endswith("removed.nex"))):
            paths.append(os.path.join(
                    gekgo_util.ECOEVOLITY_ALIGNMENT_DIR,
                    file_name))
    return paths
                
def arg_is_file(path):
    try:
        if not os.path.isfile(path):
            raise
    except:
        msg = '{0!r} is not a file'.format(path)
        raise argparse.ArgumentTypeError(msg)
    return path

def main(argv = sys.argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('nexus_paths',
            metavar = 'NEXUS-PATH',
            nargs = '+',
            type = arg_is_file,
            help = ('Paths to nexus alignment files.'))
    if argv == sys.argv:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)

    # load database
    db = SampleDatabase(path=gekgo_util.DB_PATH)
    msg_samples = get_msg_samples(db)

    # get samples used in ecoevolity analyses
    ecoevolity_samples, seq_labels = get_samples_from_nexus_files(
            msg_samples,
            args.nexus_paths)
    # write samples to stdout 
    ecoevolity_samples.write_flat_file_to_stream(
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
            keys = seq_labels)

    
if __name__ == '__main__':
    main()
