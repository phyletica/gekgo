#! /usr/bin/env python

import os
import sys
import logging
import re
import csv
import itertools
import copy

import gekgo_util
from gekgo_util import RunLogger
from data_classes import *

_LOG = RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

def get_dict_reader(file_obj, delimiter='\t'):
    if isinstance(file_obj, str):
        return (csv.DictReader(open(file_obj, 'rU'), delimiter=delimiter),
                os.path.basename(file_obj))
    else:
        return (csv.DictReader(file_obj, delimiter=delimiter),
                os.path.basename(file_obj.name))

def parse_candidates(file_obj, delimiter='\t', samples=SampleDatabase()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        s = Sample(field_series = line_dict['field_series'],
                   field_number = line_dict['field_number'])
        samples.add(s)
    return samples

def get_subset(samples, candidate_file_path):
    use_samples = SampleDatabase()
    candidates = parse_candidates(candidate_file_path, samples=SampleDatabase())
    for id in candidates.keys():
        if not samples.has_key(id):
            raise Exception('samples do not contain candidate {0}'.format(
                    id))
        new_sample = copy.deepcopy(samples[id])
        use_samples.add(new_sample)
    return use_samples

def summarize_island_sampling_for_species(species, samples):
    islands = {}
    total = 0
    for field_id, sample in samples.iteritems():
        if sample.species == species:
            if sample.island:
                islands[sample.island] = islands.get(sample.island, 0) + 1
            else:
                islands['other'] = islands.get('other', 0) + 1
            total += 1
    islands['total'] = total
    return islands

def summarize_island_sampling(samples):
    species_island_dict = {}
    for sp in samples.species:
        species_island_dict[sp] = summarize_island_sampling_for_species(
                species=sp, samples=samples)
    return species_island_dict

def write_island_sampling(samples, path):
    species_island_dict = summarize_island_sampling(samples)
    out = open(path, 'w')
    for species in sorted(species_island_dict.keys()):
        out.write("%s (%d):\n" % (species, species_island_dict[species].pop('total', 0)))
        for island in sorted(species_island_dict[species].keys()):
            out.write("\t%s: %d\n" % (island, species_island_dict[species][island]))
    out.close()

def main():
    # inputs
    path_to_candidates_in = os.path.join(gekgo_util.SUBSET_SRC_DIR,
            "candidate_samples.txt")
    path_to_lee_in = os.path.join(gekgo_util.SUBSET_SRC_DIR, "lee_list.txt")
    path_to_ku_pull_in = os.path.join(gekgo_util.SUBSET_SRC_DIR,
            "ku_pull_list.txt")
    path_to_ku_use_in = os.path.join(gekgo_util.SUBSET_SRC_DIR,
            "ku_use_list.txt")
    # outputs
    path_to_island_summary = os.path.join(gekgo_util.SUMMARIES_DIR,
            "species_sampling_by_island.txt")
    path_to_candidates_out = os.path.join(gekgo_util.SUBSETS_DIR,
            "candidate_tissues.txt")
    path_to_lee_out = os.path.join(gekgo_util.SUBSETS_DIR,
            "lsuhc_request.txt")
    path_to_ku_pull_out = os.path.join(gekgo_util.SUBSETS_DIR,
            "ku_freezer_pull.txt")
    path_to_ku_use_out = os.path.join(gekgo_util.SUBSETS_DIR,
            "ku_freezer_use.txt")

    # load database
    db = SampleDatabase(path=gekgo_util.DB_PATH)

    candidates = get_subset(db, path_to_candidates_in)
    lsuhc = get_subset(db, path_to_lee_in)
    ku_pull = get_subset(db, path_to_ku_pull_in)
    ku_use = get_subset(db, path_to_ku_use_in)

    write_island_sampling(samples=db, path=path_to_island_summary)
    # write all candidates
    candidates.write_flat_file(path=path_to_candidates_out)
    # write lsuhc request
    lsuhc.write_flat_file(path=path_to_lee_out)
    # write ku freezer pull list
    ku_pull.write_flat_file(
               path=path_to_ku_pull_out, 
               fields=['box',
                       'cell',
                       'catalog_series', 
                       'catalog_number',
                       'field_series',
                       'field_number',
                       'genus',
                       'epithet',
                       'country',
                       'island',
                       'paic',
                       'locality',
                       'lat',
                       'long',
                       'tissue',
                       'cam_extract',
                       'date',
                       'source',])
    # write ku freezer use list
    ku_use.write_flat_file(path=path_to_ku_use_out)

if __name__ == '__main__':
    main()
