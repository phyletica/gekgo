#! /usr/bin/env python

import os
import sys
import logging
import re
import csv
import itertools

import gekgo_util
from gekgo_util import RunLogger
from data_classes import *

_LOG = RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

FIELD_ID_PATTERN = re.compile(r'^\s*([a-zA-Z -/]+)\s*([0-9]+)[a-zA-Z]{0,1}\s*$')
ISLAND_FIXES = {'dayog/luzon': 'Luzon',
         'emalaysia': 'Malaysia',
         'emindanaocorr': 'Mindanao',
         'babay/leyte': 'Leyte',
         'taft/samar': 'Samar',
         'aningalan/mindoro': 'Mindoro',
         'dumgte/negros': 'Negros',
         'mindoro/dayog': 'Mindoro',
         'pandan/panay': 'Panay',
         'palawan/samarinana': 'Palawan',
         'caluya/semirara': 'Caluya'}

def my_str(x):
    if x == None:
        return ''
    else:
        return str(x)

def get_dict_reader(file_obj, delimiter='\t'):
    if isinstance(file_obj, str):
        return (csv.DictReader(open(file_obj, 'rU'), delimiter=delimiter),
                os.path.basename(file_obj))
    else:
        return (csv.DictReader(file_obj, delimiter=delimiter),
                os.path.basename(file_obj.name))

def parse_catalog_data(file_obj, delimiter='\t', samples=GekkonidSamples()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        sp = line_dict['Species/FullTaxonName'].split(' ')
        if line_dict['Date Collected'] == '':
            day = month = year = ''
        else:
            date = line_dict['Date Collected'].split('/')
            assert len(date) == 3, "could not parse date '%s' at line '%d'" % \
                    (line_dict['Date Collected'], n+1)
            day, month, year = date
        m = FIELD_ID_PATTERN.match(line_dict['Field#'])
        if not m:
            raise Exception("could not parse field id '%s' at line '%d'" % \
                (line_dict['Field#'], n+1))
        field_series, field_number = m.groups()
        loc = "; ".join([line_dict['State'],
                         line_dict['County'],
                         line_dict['LocalityName']])
        locality = loc.strip().strip(';').strip()
        s = Sample(field_series = field_series,
                   field_number = field_number,
                   genus = sp[0].strip(),
                   epithet = " ".join(sp[1:]),
                   day = day,
                   month = month,
                   year = year,
                   country = line_dict['Country'].strip(),
                   island = line_dict['Island'].strip(),
                   paic = line_dict['IslandGroup'].strip(),
                   locality = locality,
                   lat = line_dict['Latitude1'].strip(),
                   long = line_dict['Longitude1'].strip(),
                   catalog_series = 'KU',
                   catalog_number = line_dict['Catalog#'].strip(),
                   source = src)
        samples.add(s)
    return samples

def parse_extraction_data(file_obj, delimiter='\t', samples=GekkonidSamples()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        m = FIELD_ID_PATTERN.match(line_dict['Field#'])
        field_series, field_number = m.groups()
        if line_dict['Genus'].lower().startswith('ge'):
            genus = 'Gekko'
        elif line_dict['Genus'].lower().startswith('cy'):
            genus = 'Cyrtodactylus'
        else:
            raise Exception("could not parse genus '%s' at line '%d'" % \
                    line_dict['Genus'], n+1)
        s = Sample(field_series = field_series,
                   field_number = field_number,
                   genus = genus,
                   epithet = line_dict['Species'].strip(),
                   extract_cell = line_dict['Ext Cell'].strip(),
                   extract = True,
                   country = line_dict['Country'].strip(),
                   island = line_dict['Island'].strip(),
                   source = src)
        samples.add(s)
    return samples

def parse_freezer_data(file_obj, delimiter='\t', samples=GekkonidSamples()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        pass

def parse_lsuhc_data(file_obj, delimiter='\t', samples=GekkonidSamples()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        pass

def parse_taxonomic_corrections(file_obj, delimiter='\t', samples=GekkonidSamples()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        pass

def write_data(samples, path, delimiter='\t'):
    out = open(path, 'w')
    fields = ['catalog_series', 
              'catalog_number',
              'field_series',
              'field_number',
              'genus',
              'epithet',
              'country',
              'island',
              'extract',
              'date',
              'source',]
    out.write("%s\n" % delimiter.join(fields))
    for field_id, sample in samples.iteritems():
        out.write("%s\n" % delimiter.join([my_str(getattr(sample, x, '')) for x in fields]))
    out.close()

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
    sample_dir = gekgo_util.SAMPLE_DIR
    # inputs
    path_to_ku_data = os.path.join(sample_dir, "ku_gekkonid_tissues.txt")
    path_to_lab_data = os.path.join(sample_dir, "gekkonid_lab_work.txt")
    # outputs
    path_to_island_summary = os.path.join(sample_dir, "species_sampling_by_island.txt")
    path_to_all_data = os.path.join(sample_dir, "all_tissue_holdings.txt")

    data = GekkonidSamples()
    parse_catalog_data(path_to_ku_data, delimiter='\t', samples=data)
    parse_extraction_data(path_to_lab_data, delimiter='\t', samples=data)
    write_island_sampling(samples=data, path=path_to_island_summary)
    write_data(samples=data, path=path_to_all_data)

if __name__ == '__main__':
    main()