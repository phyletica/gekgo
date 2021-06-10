#! /usr/bin/env python

import os
import sys
import get_sample_table_from_nexus_files

import gekgo_util
from data_classes import Sample, SampleDatabase, Tissue, DnaExtraction


def get_phycoeval_alignment_paths():
    align_dir = os.path.join(
            gekgo_util.PROJECT_DIR,
            "full_method",
            "full-method-params-scripts",
            "nexus-alignments")
    align_files = (
            "Cyrtodactylus-reduced5_n27-polyallelic-sites-removed.nex",
            "Gekko-reduced4_n26-polyallelic-sites-removed.nex"
            )
    paths = []
    for file_name in align_files:
        paths.append(os.path.join(
                align_dir,
                file_name))
    return paths
                

if __name__ == '__main__':
    nexus_paths = get_phycoeval_alignment_paths()
    get_sample_table_from_nexus_files.main(sorted(nexus_paths))
