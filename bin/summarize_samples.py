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

FIELD_ID_PATTERN = re.compile(r'^\s*([a-z-A-Z]+)\s*([0-9]+)\s*$')
            
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
        s = Sample(field_series = field_series,
                   field_number = field_number,
                   genus = sp[0].strip(),
                   epithet = " ".join(sp[1:]),
                   day = day,
                   month = month,
                   year = year,
                   country = line_dict['Country'].strip(),
                   island = line_dict['Island'].strip(),
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

