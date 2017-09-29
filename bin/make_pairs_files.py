#! /usr/bin/env python

import os
import sys
import logging
import re
import csv
import itertools
import copy
import math

import gekgo_util
from gekgo_util import RunLogger, get_dict_reader
from data_classes import Sample, SampleDatabase, Tissue, DnaExtraction

_LOG = RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

def get_one(samples):
    return 1

def get_half_samples(samples):
    return int(math.ceil(len(samples) / 2.0))

def get_msg_samples(sample_db):
    samples = SampleDatabase()
    for k, sample in sample_db.iteritems():
        if sample.extraction.plate != None:
            new_sample = copy.deepcopy(sample)
            samples.add(new_sample)
    return samples

def get_seq_label(sample):
    l = "_".join((sample.seq_label,
            sample.genus,
            sample.epithet.replace(' ', '').replace('/', '.')))
    if sample.island:
        l = l +  "_" + sample.island.replace(' ','').replace('/', '.')
    else:
        l = l +  "_" + sample.country.replace(' ','').replace('/', '.')
    return l

def get_island_samples(sample_db,
        genus,
        epithet,
        island,
        locality_name = "",
        omit = []):
    samples = SampleDatabase()
    for k, sample in sample_db.iteritems():
        if sample.seq_label in omit:
            continue
        if (sample.genus == genus and
                sample.epithet == epithet and
                sample.island == island and
                locality_name in sample.locality):
            new_sample = copy.deepcopy(sample)
            samples.add(new_sample)
    return samples

def get_samples(sample_db, genus):
    samples = SampleDatabase()
    for k, sample in sample_db.iteritems():
        if sample.genus == genus:
            new_sample = copy.deepcopy(sample)
            samples.add(new_sample)
    return samples

def write_pair_file(pop1_samples, pop2_samples,
        min_pop_sample_func = get_one):
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
    pair_str += "\n# {p1}:{n1} {p2}:{n2}\n".format(
            p1 = pop1_island.replace(' ', '').replace('/', '.'),
            n1 = min_pop_sample_func(pop1_samples),
            p2 = pop2_island.replace(' ', '').replace('/', '.'),
            n2 = min_pop_sample_func(pop2_samples),
            )
    with open(path, "w") as out:
        out.write(pair_str)
    return

def write_samples_file(samples,
        min_pop_sample_func = get_half_samples):
    genus = samples.values()[0].genus
    path = "samples-{genus}.txt".format(
            genus = genus,
            )
    with open(path, "w") as out:
        for sample in samples.values():
            out.write("{0}\t{1}\n".format(get_seq_label(sample), genus))
        out.write("\n# {g}:{n}\n".format(
                g = genus,
                n = min_pop_sample_func(samples)))
    return

def main():
    omit = [
            # Cyrt
            "RMB_14249",
            "CDS_1768",
            "PNM.CMNH_1289",
            "PNM.CMNH_1292",
            "PNM.CMNH_1293",
            "PNM.CMNH_1298",
            "RMB_11309",
            "RMB_15211",
            "RMB_15052",
            "RMB_14956",
            "RMB_5907",
            "RMB_7722",
            "RMB_11229",
            "CDS_4342",
            # Gekko
            "CDS_1459",
            "CDS_754",
            "RMB_8765",
            ]

    # load database
    db = SampleDatabase(path=gekgo_util.DB_PATH)
    msg_samples = get_msg_samples(db)

    cyrt = get_samples(msg_samples, genus = "Cyrtodactylus")
    write_samples_file(cyrt)
    gekko = get_samples(msg_samples, genus = "Gekko")
    write_samples_file(gekko)

    cyrt_annulatus_bohol = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "annulatus",
            island = "Bohol",
            omit = omit)
    cyrt_annulatus_camiguin_sur = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "annulatus",
            island = "Camiguin Sur",
            omit = omit)
    cyrt_annulatus_mindanao_west = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "annulatus",
            island = "Mindanao",
            locality_name = "Pasonanca",
            omit = omit)
    cyrt_annulatus_mindanao_east = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "annulatus",
            island = "Mindanao",
            locality_name = "Calinan",
            omit = omit)
    write_pair_file(
            pop1_samples = cyrt_annulatus_bohol,
            pop2_samples = cyrt_annulatus_camiguin_sur,
            min_pop_sample_func = get_one)


    cyrt_balu = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "baluensis",
            island = "Kinabalu",
            omit = omit)
    cyrt_redi = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "redimiculus",
            island = "Palawan",
            omit = omit)
    write_pair_file(
            pop1_samples = cyrt_balu,
            pop2_samples = cyrt_redi,
            min_pop_sample_func = get_one)


    cyrt_gubaot = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "gubaot",
            island = "Leyte",
            omit = omit)
    cyrt_sumuroi = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "sumuroi",
            island = "Samar",
            omit = omit)
    write_pair_file(
            pop1_samples = cyrt_gubaot,
            pop2_samples = cyrt_sumuroi,
            min_pop_sample_func = get_one)


    cyrt_phil_babuyan_claro = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Babuyan Claro",
            omit = omit)
    cyrt_phil_luzon_magrafil = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Luzon",
            locality_name = "Barangay Magrafil",
            omit = omit)
    write_pair_file(
            pop1_samples = cyrt_phil_babuyan_claro,
            pop2_samples = cyrt_phil_luzon_magrafil,
            min_pop_sample_func = get_one)


    cyrt_phil_camiguin_norte = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Camiguin Norte",
            omit = omit)
    cyrt_phil_luzon_ilocos = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Luzon",
            locality_name = "Ilocos Norte",
            omit = omit)
    write_pair_file(
            pop1_samples = cyrt_phil_camiguin_norte,
            pop2_samples = cyrt_phil_luzon_ilocos,
            min_pop_sample_func = get_one)


    cyrt_phil_luzon = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Luzon",
            locality_name = "Laguna",
            omit = omit)
    cyrt_phil_polillo = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Polillo",
            omit = omit)
    write_pair_file(
            pop1_samples = cyrt_phil_luzon,
            pop2_samples = cyrt_phil_polillo,
            min_pop_sample_func = get_one)


    cyrt_phil_negros = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Negros",
            omit = omit)
    cyrt_phil_panay = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Panay",
            omit = omit)
    write_pair_file(
            pop1_samples = cyrt_phil_negros,
            pop2_samples = cyrt_phil_panay,
            min_pop_sample_func = get_one)


    cyrt_phil_sibuyan = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Sibuyan",
            omit = omit)
    cyrt_phil_tablas = get_island_samples(msg_samples,
            genus = "Cyrtodactylus",
            epithet = "philippinicus",
            island = "Tablas",
            omit = omit)
    write_pair_file(
            pop1_samples = cyrt_phil_sibuyan,
            pop2_samples = cyrt_phil_tablas,
            min_pop_sample_func = get_one)




    gekko_crombota_babuyan_claro = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "crombota",
            island = "Babuyan Claro",
            omit = omit)
    gekko_rossi_calayan = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "rossi",
            island = "Calayan",
            omit = omit)
    write_pair_file(
            pop1_samples = gekko_crombota_babuyan_claro,
            pop2_samples = gekko_rossi_calayan,
            min_pop_sample_func = get_one)


    gekko_mind_caluya = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Caluya",
            omit = omit)
    gekko_mind_mindoro = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Mindoro",
            locality_name = "Formon",
            omit = omit)
    write_pair_file(
            pop1_samples = gekko_mind_caluya,
            pop2_samples = gekko_mind_mindoro,
            min_pop_sample_func = get_one)


    gekko_mind_lubang = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Lubang",
            omit = omit)
    gekko_mind_luzon = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Luzon",
            locality_name = "Laguna",
            omit = omit)
    write_pair_file(
            pop1_samples = gekko_mind_lubang,
            pop2_samples = gekko_mind_luzon,
            min_pop_sample_func = get_one)


    gekko_mind_maestre = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Maestre De Campo",
            omit = omit)
    gekko_mind_masbate = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Masbate",
            omit = omit)
    write_pair_file(
            pop1_samples = gekko_mind_maestre,
            pop2_samples = gekko_mind_masbate,
            min_pop_sample_func = get_one)


    gekko_mind_negros = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Negros",
            locality_name = "Sipalay",
            omit = omit)
    gekko_mind_panay = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "mindorensis",
            island = "Panay",
            locality_name = "Pilar",
            omit = omit)
    write_pair_file(
            pop1_samples = gekko_mind_negros,
            pop2_samples = gekko_mind_panay,
            min_pop_sample_func = get_one)


    gekko_porosus_batan = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "porosus",
            island = "Batan",
            omit = omit)
    gekko_porosus_sabtang = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "porosus",
            island = "Sabtang",
            omit = omit)
    write_pair_file(
            pop1_samples = gekko_porosus_batan,
            pop2_samples = gekko_porosus_sabtang,
            min_pop_sample_func = get_one)


    gekko_romblon_romblon = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "romblon",
            island = "Romblon",
            omit = omit)
    gekko_romblon_tablas = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "romblon",
            island = "Tablas",
            omit = omit)
    write_pair_file(
            pop1_samples = gekko_romblon_romblon,
            pop2_samples = gekko_romblon_tablas,
            min_pop_sample_func = get_one)


    gekko_a_dalupiri = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "sp. a",
            island = "Dalupiri",
            omit = omit)
    gekko_b_camiguin_norte = get_island_samples(msg_samples,
            genus = "Gekko",
            epithet = "sp. b",
            island = "Camiguin Norte",
            omit = omit)
    write_pair_file(
            pop1_samples = gekko_a_dalupiri,
            pop2_samples = gekko_b_camiguin_norte,
            min_pop_sample_func = get_one)


if __name__ == '__main__':
    main()
