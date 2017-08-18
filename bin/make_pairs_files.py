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

def get_msg_samples(sample_db):
    samples = SampleDatabase()
    for k, sample in sample_db.iteritems():
        if sample.extraction.plate != None:
            new_sample = copy.deepcopy(sample)
            samples.add(new_sample)
    return samples

def get_seq_label(sample):
    return "_".join((sample.seq_label,
            sample.genus,
            sample.epithet.replace(' ', '').replace('/', '.'),
            sample.island.replace(' ','').replace('/', '.')))


def get_island_samples(sample_db,
        genus,
        epithet,
        island,
        locality_name = ""):
    samples = SampleDatabase()
    for k, sample in sample_db.iteritems():
        if (sample.genus == genus and
                sample.epithet == epithet and
                sample.island == island and
                locality_name in sample.locality):
            new_sample = copy.deepcopy(sample)
            samples.add(new_sample)
    return samples

def write_pair_file(pop1_samples, pop2_samples):
    genus = pop1_samples.values()[0].genus
    pop1_epithet = pop1_samples.values()[0].epithet
    pop1_island =  pop1_samples.values()[0].island
    pop2_epithet = pop2_samples.values()[0].epithet
    pop2_island =  pop2_samples.values()[0].island
    path = "samples-{genus}-{sp1}-{sp2}-{isl1}-{isl2}.txt".format(
            genus = genus,
            sp1 = pop1_epithet.replace(' ', '').replace('/', '.'),
            sp2 = pop2_epithet.replace(' ', '').replace('/', '.'),
            isl1 = pop1_island.replace(' ', '').replace('/', '.'),
            isl2 = pop2_island.replace(' ', '').replace('/', '.'),
            )
    pair_str = ""
    for sample in pop1_samples.values():
        assert sample.genus == genus
        assert sample.epithet == pop1_epithet
        assert sample.island == pop1_island
        pair_str += "{0}\t{1}\n".format(
                get_seq_label(sample),
                sample.island.replace(' ','').replace('/', '.'))
    for sample in pop2_samples.values():
        assert sample.genus == genus
        assert sample.epithet == pop2_epithet
        assert sample.island == pop2_island
        pair_str += "{0}\t{1}\n".format(
                get_seq_label(sample),
                sample.island.replace(' ','').replace('/', '.'))
    pair_str += "\n# {0}:1 {1}:1\n".format(
            pop1_island.replace(' ', '').replace('/', '.'),
            pop2_island.replace(' ', '').replace('/', '.'))
    with open(path, "w") as out:
        out.write(pair_str)
    return

def main():
    # load database
    db = SampleDatabase(path=gekgo_util.DB_PATH)
    msg_samples = get_msg_samples(db)

    cyrt_annulatus_bohol = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "annulatus",
            island = "Bohol")
    cyrt_annulatus_camiguin_sur = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "annulatus",
            island = "Camiguin Sur")
    cyrt_annulatus_mindanao_west = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "annulatus",
            island = "Mindanao",
            locality_name = "Pasonanca")
    cyrt_annulatus_mindanao_east = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "annulatus",
            island = "Mindanao",
            locality_name = "Calinan")
    
    write_pair_file(
            pop1_samples = cyrt_annulatus_camiguin_sur,
            pop2_samples = cyrt_annulatus_mindanao_east)

    cyrt_gubaot = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "gubaot",
            island = "Leyte")
    cyrt_sumuroi = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "sumuroi",
            island = "Samar")

    write_pair_file(
            pop1_samples = cyrt_gubaot,
            pop2_samples = cyrt_sumuroi)

    cyrt_phil_luzon = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Luzon",
            locality_name = "Laguna")
    cyrt_phil_polillo = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Polillo")

    write_pair_file(
            pop1_samples = cyrt_phil_luzon,
            pop2_samples = cyrt_phil_polillo)

    cyrt_phil_sibuyan = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Sibuyan")
    cyrt_phil_tablas = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Tablas")

    write_pair_file(
            pop1_samples = cyrt_phil_sibuyan,
            pop2_samples = cyrt_phil_tablas)

    cyrt_phil_negros = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Negros")
    cyrt_phil_panay = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Panay")

    write_pair_file(
            pop1_samples = cyrt_phil_negros,
            pop2_samples = cyrt_phil_panay)

    gekko_mind_negros = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Negros")
    gekko_mind_panay = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Panay")

    write_pair_file(
            pop1_samples = gekko_mind_negros,
            pop2_samples = gekko_mind_panay)

    gekko_porosus_batan = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "porosus",
            island = "Batan")
    gekko_porosus_sabtang = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "porosus",
            island = "Sabtang")

    write_pair_file(
            pop1_samples = gekko_porosus_batan,
            pop2_samples = gekko_porosus_sabtang)

    gekko_romblon_romblon = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "romblon",
            island = "Romblon")
    gekko_romblon_tablas = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "romblon",
            island = "Tablas")

    write_pair_file(
            pop1_samples = gekko_romblon_romblon,
            pop2_samples = gekko_romblon_tablas)

    gekko_a_dalupiri = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "sp. a",
            island = "Dalupiri")
    gekko_b_camiguin_norte = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "sp. b",
            island = "Camiguin Norte")

    write_pair_file(
            pop1_samples = gekko_a_dalupiri,
            pop2_samples = gekko_b_camiguin_norte)



    # Dispersal pairs
    gekko_mind_lubang = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Lubang")
    gekko_mind_luzon = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Luzon",
            locality_name = "Laguna")

    write_pair_file(
            pop1_samples = gekko_mind_lubang,
            pop2_samples = gekko_mind_luzon)

    gekko_mind_caluya = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Caluya")
    gekko_mind_mindoro = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Mindoro",
            locality_name = "Formon")

    write_pair_file(
            pop1_samples = gekko_mind_caluya,
            pop2_samples = gekko_mind_mindoro)

    gekko_mind_maestre = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Maestre De Campo")
    gekko_mind_masbate = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Masbate")

    write_pair_file(
            pop1_samples = gekko_mind_maestre,
            pop2_samples = gekko_mind_masbate)

if __name__ == '__main__':
    main()

