#! /usr/bin/env python

import os
import sys
import get_sample_table_from_nexus_files

import gekgo_util
from data_classes import Sample, SampleDatabase, Tissue, DnaExtraction


def get_ecoevolity_alignment_paths():
    paths = []
    for file_name in os.listdir(gekgo_util.ECOEVOLITY_ALIGNMENT_DIR):
        if ((file_name.endswith(".nex")) and
                (not file_name.endswith("removed.nex")) and
                (not "mindorensis-MaestreDeCampo-Masbate" in file_name) and
                (not "mindorensis-Caluya-Mindoro" in file_name)):
            paths.append(os.path.join(
                    gekgo_util.ECOEVOLITY_ALIGNMENT_DIR,
                    file_name))
    return paths
                

if __name__ == '__main__':
    nexus_paths = get_ecoevolity_alignment_paths()
    get_sample_table_from_nexus_files.main(sorted(nexus_paths))
