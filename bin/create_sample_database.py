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

FIELD_ID_PATTERN = re.compile(r'^\s*([a-zA-Z -/]+)\s*([0-9]+)[a-zA-Z]{0,1}\s*$')
PULAU_PATTERN = re.compile(r'pulau([a-z -]+),*', re.IGNORECASE)
ISLAND_PATTERN = re.compile(r',*([a-z -]+)island', re.IGNORECASE)
ISLAND_FIXES = {'dayog/luzon': 'Luzon',
         'emalaysia': 'Malaysia',
         'emindanaocorr': 'Mindanao',
         'baybay/leyte': 'Leyte',
         'baybay': 'Leyte',
         'taft/samar': 'Samar',
         'taft': 'Samar',
         'aningalan/mindoro': 'Mindoro',
         'aningalan': 'Mindoro',
         'dumgte/negros': 'Negros',
         'dumaguete/negros': 'Negros',
         'dumaguete': 'Negros',
         'dumgte': 'Negros',
         'mindoro/dayog': 'Mindoro',
         'dayog': 'Mindoro',
         'pandan/panay': 'Panay',
         'pandan': 'Panay',
         'palawan/samarinana': 'Palawan',
         'caluya/semirara': 'Caluya',
         'banahaw/luzon': 'Luzon',
         'banahao': 'Luzon',
         'biak/luzon': 'Luzon',
         'naga/luzon': 'Luzon'}

def get_dict_reader(file_obj, delimiter='\t'):
    if isinstance(file_obj, str):
        return (csv.DictReader(open(file_obj, 'rU'), delimiter=delimiter),
                os.path.basename(file_obj))
    else:
        return (csv.DictReader(file_obj, delimiter=delimiter),
                os.path.basename(file_obj.name))

def apply_island_fixes(samples):
    for field_id, sample in samples.iteritems():
        if sample.island:
            isl = sample.island
            i = isl.lower()
            if i in ISLAND_FIXES.keys():
                del sample.island
                sample.island = ISLAND_FIXES[i]

def parse_catalog_data(file_obj, delimiter='\t', samples=SampleDatabase()):
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
        locality = loc.strip(' ;')
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

def parse_cam_extraction_data(file_obj, delimiter='\t', samples=SampleDatabase()):
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
        catalog_series = None
        catalog_number = None
        fs = field_series.upper().replace(' ', '')
        if fs == 'LSUHC' or fs == 'LG' or fs == 'LLG':
            field_series = 'LSUHC'
            catalog_series = 'LSUHC'
            catalog_number = field_number
        s = Sample(field_series = field_series,
                   field_number = field_number,
                   catalog_series = catalog_series,
                   catalog_number = catalog_number,
                   genus = genus,
                   epithet = line_dict['Species'].strip(),
                   cam_extract_cell = line_dict['Ext Cell'].strip(),
                   cam_extract = True,
                   country = line_dict['Country'].strip(),
                   island = line_dict['Island'].strip(),
                   source = src)
        samples.add(s)
    return samples

def parse_freezer_data(file_obj, delimiter='\t', samples=SampleDatabase(),
                       skip_bad_field_ids=False):
    no_id_pattern = re.compile(r'\s*no\s*number\s*', re.IGNORECASE)
    no_field_series_pattern = re.compile(r'\s*([0-9]+)\s*')
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    no_id_count = 0
    rmb_x_count = 0
    for n, line_dict in enumerate(dr):
        m = FIELD_ID_PATTERN.match(line_dict['Field Number'])
        if not m:
            m_no_id = no_id_pattern.match(line_dict['Field Number'])
            m_no_series = no_field_series_pattern.match(line_dict['Field Number'])
            if m_no_id or line_dict['Field Number'].strip() == '':
                field_series = 'NOID'
                field_number = no_id_count
                no_id_count += 1
            elif m_no_series:
                field_series = 'NOSERIES'
                field_number = m_no_series.groups()[0]
            elif line_dict['Field Number'].strip().lower().replace(' ', '') == \
                    'rmbxxx':
                field_series = 'RMB'
                field_number = rmb_x_count
                rmb_x_count += 1
            else:
                if skip_bad_field_ids:
                    _LOG.warning("could not parse field id {0!r} at line {1}"
                              "... skipping!".format(
                            line_dict['Field Number'], n+1))
                else:
                    raise Exception("could not parse field id {0!r} at "
                                    "line {1}".format(
                            line_dict['Field Number'], n+1))
        else:
            field_series, field_number = m.groups()
        catalog_series = None
        catalog_number = None
        fs = field_series.upper().replace(' ', '')
        if fs == 'LSUHC' or fs == 'LG' or fs == 'LLG':
            field_series = 'LSUHC'
            catalog_series = 'LSUHC'
            catalog_number = field_number
        loc = "; ".join([line_dict['Province'],
                         line_dict['Municipality'],
                         line_dict['Barangay'],
                         line_dict['Local Area Name'],
                         line_dict['Column1'],
                         line_dict['Column2']])
        locality = loc.strip(' ;')
        s = Sample(field_series = field_series,
                   field_number = field_number,
                   catalog_series = catalog_series,
                   catalog_number = catalog_number,
                   locality = locality,
                   tower = line_dict['Tower'].strip(),
                   box = line_dict['Box'].strip(),
                   cell = line_dict['Cell'].strip(),
                   genus = line_dict['Genus'].strip(),
                   epithet = line_dict['Species'].strip(),
                   country = line_dict['Country'].strip(),
                   island = line_dict['Island'].strip(),
                   source = src)
        samples.add(s)
    return samples

def parse_lsuhc_data(file_obj, delimiter='\t', samples=SampleDatabase()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        sp = line_dict['Species'].split(' ')
        genus = sp[0].strip()
        epithet = None
        if len(sp) > 1:
            epithet = " ".join(sp[1:])
        locality = line_dict['Locality']
        island = None
        mi = ISLAND_PATTERN.search(locality)
        mp = PULAU_PATTERN.search(locality)
        if mi:
            island = mi.groups()[0].strip() + ' island'
        if mp:
            island = 'pulau ' + mp.groups()[0].strip()
        country = None
        if locality:
            country = locality.split(',')[0]
        s = Sample(field_series = 'LSUHC',
                   catalog_series = 'LSUHC',
                   field_number = line_dict['Cat. No.'].strip(),
                   catalog_number = line_dict['Cat. No.'].strip(),
                   genus = genus,
                   epithet = epithet,
                   country = country,
                   island = island,
                   locality = locality,
                   source = src)
        samples.add(s)
    return samples

def parse_taxonomic_corrections(file_obj, delimiter='\t', samples=SampleDatabase()):
    dr, src = get_dict_reader(file_obj, delimiter=delimiter)
    for n, line_dict in enumerate(dr):
        s = Sample(field_series = line_dict['field_series'],
                   field_number = line_dict['field_number'],
                   genus = line_dict['genus'],
                   epithet = line_dict['epithet'],
                   country = line_dict['country'],
                   island = line_dict['island'])
        samples.add(s)
    return samples

def get_missing_tissue_locations(gekkonid_samples, gekkonid_samples_db):
    for id, sample in gekkonid_samples.iteritems():
        if ((sample.tissue == None) and 
            (gekkonid_samples_db.has_key(id)) and
            (gekkonid_samples_db[id].tissue != None)):
            _LOG.info('found tissue location for {0}: {1}'.format(id,
                    gekkonid_samples_db[id].tissue))
            sample.tower = gekkonid_samples_db[id].tower
            sample.box = gekkonid_samples_db[id].box
            sample.cell = gekkonid_samples_db[id].cell

def main():
    if os.path.exists(gekgo_util.DB_PATH):
        _LOG.error('Database already exists!\n'
                'If you want to use or modify this database, use a separate\n'
                'script. This scripts sole purpose is to create the database\n'
                'from scratch.')
        sys.exit(-1)
    sample_dir = gekgo_util.SAMPLE_DIR
    source_dir = os.path.join(sample_dir, "sources")
    # inputs
    path_to_ku_data = os.path.join(source_dir, "ku_gekkonid_tissues.txt")
    path_to_lab_data = os.path.join(source_dir, "gekkonid_lab_work.txt")
    path_to_lsuhc_data = os.path.join(source_dir, "LSUHC_geckos.txt")
    path_to_freezer_data = os.path.join(source_dir, "ku_freezer.txt")
    path_to_full_freezer_db = os.path.join(source_dir, "ku_freezer_all.txt")
    path_to_corrections = os.path.join(source_dir, "taxonomic_fixes.txt")

    cat_data = parse_catalog_data(path_to_ku_data, delimiter='\t',
            samples=SampleDatabase())
    lab_data = parse_cam_extraction_data(path_to_lab_data, delimiter='\t',
            samples=SampleDatabase())
    lsuhc_data = parse_lsuhc_data(path_to_lsuhc_data, delimiter='\t',
            samples=SampleDatabase())
    freezer_data = parse_freezer_data(path_to_freezer_data, delimiter='\t',
            samples=SampleDatabase())
    fix_data = parse_taxonomic_corrections(path_to_corrections, delimiter='\t',
            samples=SampleDatabase())

    cat_data.merge(lab_data, overwrite=False)
    cat_data.merge(lsuhc_data, overwrite=True)
    freezer_data.merge(cat_data, overwrite=True)
    freezer_data.merge(fix_data, overwrite=True)
    apply_island_fixes(freezer_data)

    _LOG.info('\nPARSING FREEZER DATABASE\n')
    freezer_db = parse_freezer_data(path_to_full_freezer_db, delimiter='\t',
            skip_bad_field_ids=True)
    _LOG.info('\nCHECKING FOR MISSING TISSUE LOCATIONS\n')
    _LOG.info('length of samples: {0}'.format(len(freezer_data)))
    _LOG.info('length of data base: {0}'.format(len(freezer_db)))
    get_missing_tissue_locations(gekkonid_samples=freezer_data,
            gekkonid_samples_db=freezer_db)

    freezer_data.path = gekgo_util.DB_PATH
    freezer_data.commit()

if __name__ == '__main__':
    main()
