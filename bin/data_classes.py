#! /usr/bin/env python

import os
import sys
import logging
import re
import datetime
import copy
try:
    import cPickle as pickle
except ImportError:
    import pickle

import gekgo_util
from gekgo_util import RunLogger

_LOG = RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

def my_str(x):
    if x == None:
        return ''
    else:
        return str(x)

def my_getattr(obj, string):
    queries = string.split('.')
    for q in queries:
        obj = getattr(obj, q, None)
    return obj

class SampleDatabase(dict):
    """
    A dictionary of Gekkonid Sample instances.
    """
    def __init__(self, path=None):
        self.path = path
        self._species_set = set()
        if path and os.path.exists(self.path):
            _LOG.info('Database {0!r} already exists... '
                      'reading in data'.format(self.path))
            stream = open(self.path, 'rb')
            db = pickle.load(stream)
            stream.close()
            assert self.path == db.path
            dict.__init__(self, db)
            self._species_set = db._species_set
        else:
            _LOG.info('Starting new database')
            dict.__init__(self)
        self._update_species_set()

    def _get_directory(self):
        if self.path:
            return os.path.dirname(self.path)
        else:
            return None

    directory = property(_get_directory)

    def _get_flat_file_path(self):
        if self.path:
            return os.path.join(self.directory, 'flat_data.txt')
        else:
            return None

    flat_file_path = property(_get_flat_file_path)

    def commit(self):
        if self.path:
            _LOG.info('Writing database to {0!r}'.format(self.path))
            try:
                stream = open(self.path, 'wb')
            except Exception:
                _LOG.error('Cannot open path {0!r} to write database\n'
                           'Update path attribute and try again!'.format(
                                    self.path))
                return
            pickle.dump(self, stream)
            stream.close()
            self.write_flat_file(path=self.flat_file_path)
        else:
            _LOG.error('You must specify path attribute before commiting!')
        
    def _update_species_set(self):
        self._species_set = set()
        for sample in self.itervalues():
            self._species_set.add(sample.species)

    def _get_species_set(self):
        self._update_species_set()
        return self._species_set

    species = property(_get_species_set)

    def add(self, sample_object, overwrite=False):
        if not isinstance(sample_object, Sample):
            raise Exception("SampleDatabase dict only holds Sample objects.")
        if not sample_object.field_id:
            raise Exception("Sample does not have field id; cannot add.")
        if sample_object.field_id in self.keys():
            _LOG.warning(
                    "'%s' already in dict; updating this sample" % \
                    sample_object.field_id)
            self[sample_object.field_id].update(sample_object,
                    overwrite=overwrite)
            self._species_set.add(self[sample_object.field_id].species)
        else:
            self[sample_object.field_id] = sample_object
            self._species_set.add(self[sample_object.field_id].species)

    def merge(self, gekkonid_samples_obj, overwrite=False):
        for field_id, sample in gekkonid_samples_obj.iteritems():
            self.add(sample, overwrite=overwrite)

    def get_copy(self):
        new_db = SampleDatabase()
        for k, sample in self.iteritems():
            new_sample = sample.get_copy()
            new_db.add(new_sample)
        assert self.species == new_db.species
        assert len(self) == len(new_db)
        assert sorted(self.keys()) == sorted(new_db.keys())
        return new_db

    def write_flat_file(self, path, delimiter='\t',
                   fields=['catalog_series', 
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
                           'tissue_sample.found',
                           'tissue_sample.material',
                           'tissue_sample.preservative',
                           'tissue_sample.tube_data',
                           'tissue_sample.notes',
                           'extraction.protocol',
                           'extraction.rnase',
                           'extraction.qubit',
                           'extraction.notes',
                           'extraction.gel_lane',
                           'extraction.plate',
                           'extraction.row',
                           'extraction.column',
                           'extraction.msg_barcode',
                           'extraction.dilution',
                           'cam_extract',
                           'cam_extract_cell',
                           'date',
                           'source',]):
        _LOG.info('Writing database flat file to {0!r}'.format(
                path))
        out = open(path, 'w')
        out.write("%s\n" % delimiter.join(fields))
        for field_id, sample in self.iteritems():
            out.write("%s\n" % delimiter.join([
                    my_str(my_getattr(sample, x)) for x in fields]))
        out.close()  

class Tissue(object):
    def __init__(self, **kwargs):
        self.found = kwargs.pop('found', False)
        self.material = kwargs.pop('material', None)
        self.preservative = kwargs.pop('preservative', None)
        self.tube_data = kwargs.pop('tube_data', {})
        self.notes = kwargs.pop('notes', None)

    def __nonzero__(self):
        return self.found

    def get_copy(self):
        dc = copy.deepcopy(self)
        return Tissue(**dc.__dict__)

class DnaExtraction(Tissue):
    def __init__(self, **kwargs):
        self.extracted = kwargs.pop('extracted', False)
        self.protocol = kwargs.pop('protocol', None)
        self.rnase = kwargs.pop('rnase', False)
        self.nanodrop_conc = kwargs.pop('nanodrop_conc', None)
        self.nanodrop_a260 = kwargs.pop('nanodrop_a260', None)
        self.nanodrop_260_280 = kwargs.pop('nanodrop_260_280', None)
        self.nanodrop_260_230 = kwargs.pop('nanodrop_260_230', None)
        self.qubit = kwargs.pop('qubit', None)
        self.notes = kwargs.pop('notes', None)
        self.gel_lane = kwargs.pop('gel_lane', None)
        self.plate = kwargs.pop('plate', None)
        self.row = kwargs.pop('row', None)
        self.column = kwargs.pop('column', None)
        self.msg_barcode = kwargs.pop('msg_barcode', None)
        self.dilution = kwargs.pop('dilution', None)

    def __nonzero__(self):
        return self.extracted

    def get_copy(self):
        dc = copy.deepcopy(self)
        return DnaExtraction(**dc.__dict__)

class Sample(object):
    """
    An instance of Gekkonid sample data.
    """

    day_pattern = re.compile(r'^(\d{1,2})$')
    year_pattern = re.compile(r'^(\d{4})$')
    month_digit_pattern = re.compile(r'^(\d{1,2})$')
    month_letter_pattern = re.compile(r'^([a-zA-Z]{3})[a-zA-Z]*$')
    months = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
              'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
    field_series_label_conversions = [
            ('PNM/CMNH', 'PNM.CMNH'),
            ('KU-FS', 'KUFS'),
            ]

    def __init__(self, **kwargs):
        self._field_series = None
        self._field_number = None
        self._catalog_series = None
        self._catalog_number = None
        self._genus = None
        self._epithet = None
        self._country = None
        self._island = None
        self._paic = None
        self._locality = None
        self._lat = None
        self._long = None
        self._cam_extract_cell = None
        self._tower = None
        self._box = None
        self._cell = None
        self._day = None
        self._month = None
        self._year = None
        self._source = None
        self.field_series = kwargs.pop('field_series', None)
        self.field_number = kwargs.pop('field_number', None)
        self.catalog_series = kwargs.pop('catalog_series', None)
        self.catalog_number = kwargs.pop('catalog_number', None)
        self.genus = kwargs.pop('genus', None)
        self.epithet = kwargs.pop('epithet', None)
        self.country = kwargs.pop('country', None)
        self.island = kwargs.pop('island', None)
        self.paic = kwargs.pop('paic', None)
        self.locality = kwargs.pop('locality', None)
        self.lat = kwargs.pop('lat', None)
        self.long = kwargs.pop('long', None)
        self.cam_extract_cell = kwargs.pop('cam_extract_cell', None)
        self.cam_extract = kwargs.pop('cam_extract', False)
        if self.cam_extract_cell:
            self.cam_extract = True
        self.tower = kwargs.pop('tower', None)
        self.box = kwargs.pop('box', None)
        self.cell = kwargs.pop('cell', None)
        self.day = kwargs.pop('day', None)
        self.month = kwargs.pop('month', None)
        self.year = kwargs.pop('year', None)
        self.source = kwargs.pop('source', None)
        tissue_args = kwargs.pop('tissue', {})
        self.tissue_sample = Tissue(**tissue_args)
        extraction_args = kwargs.pop('extraction', {})
        self.extraction = DnaExtraction(**extraction_args)
        if len(kwargs.keys()) > 0:
            _LOG.warning("Unused kwargs passed to Sample.__init__ for '%s':\n" % \
                          self.field_id + \
                      "\t%s" % ", ".join([str(x) for x in kwargs.keys()]))

    def update(self, sample_object, overwrite=False):
        """
        Update this Sample instance with information in `sample_object.`
        If `overwrite` is False, all information is kept. If `overwrite`
        is True all new data in `sample_object` overwrites the data in this
        Sample instance.
        """

        if not isinstance(sample_object, Sample):
            raise ValueError("argument to update must be Sample object.")
        if not self.field_id or not sample_object.field_id:
            raise Exception("both Sample objects must have a field id.")
        assert self.field_number == sample_object.field_number
        if self.field_series and sample_object.field_series:
            assert self.field_series == sample_object.field_series
        if not self.field_series and sample_object.field_series:
            self.field_series = sample_object.field_series
        if self.catalog_series and sample_object.catalog_series:
            assert self.catalog_series == sample_object.catalog_series
        if not self.catalog_series and sample_object.catalog_series:
            self.catalog_series = sample_object.catalog_series
        if self.catalog_number and sample_object.catalog_number:
            assert self.catalog_number == sample_object.catalog_number, \
                "two catalog numbers given for '%s'." % self.field_id
        if not self.catalog_number and sample_object.catalog_number:
            self.catalog_number = sample_object.catalog_number
        if self.date != '' and sample_object.date != '':
            assert self.date == sample_object.date
        if self.day and sample_object.day:
            assert self.day == sample_object.day
        if not self.day and sample_object.day:
            self.day = sample_object.day
        if self.month and sample_object.month:
            assert self.month == sample_object.month
        if not self.month and sample_object.month:
            self.month = sample_object.month
        if self.year and sample_object.year:
            assert self.year == sample_object.year
        if not self.year and sample_object.year:
            self.year = sample_object.year
        if self.lat and sample_object.lat:
            assert self.lat == sample_object.lat, \
                "cannot have two latitudes for sample '%s'." % self.field_id
        if not self.lat and sample_object.lat:
            self.lat = sample_object.lat
        if self.long and sample_object.long:
            assert self.long == sample_object.long, \
                "cannot have two longitudes for sample '%s'." % self.field_id
        if not self.long and sample_object.long:
            self.long = sample_object.long
        if overwrite:
            if sample_object.genus:
                del self.genus
            if sample_object.epithet:
                del self.epithet
            if sample_object.country:
                del self.country
            if sample_object.island:
                del self.island
            if sample_object.paic:
                del self.paic
            if sample_object.locality:
                del self.locality
            if sample_object.cam_extract_cell:
                del self.cam_extract_cell
            if sample_object._tower:
                del self.tower
            if sample_object._box:
                del self.box
            if sample_object._cell:
                del self.cell
        self.genus = sample_object.genus
        self.epithet = sample_object.epithet
        self.country = sample_object.country
        self.island = sample_object.island
        self.paic = sample_object.paic
        self.locality = sample_object.locality
        self.cam_extract_cell = sample_object.cam_extract_cell
        self.tower = sample_object.tower
        self.box = sample_object.box
        self.cell = sample_object.cell
        self.source = sample_object.source

    def get_copy(self):
        new_sample = Sample(field_series = self.field_series,
                field_number = self.field_number)
        new_sample.update(self, overwrite=True)
        if hasattr(self, 'tissue_sample'):
            new_sample.tissue_sample = self.tissue_sample.get_copy()
        if hasattr(self, 'extraction'):
            new_sample.extraction = self.extraction.get_copy()
        return new_sample

    def _get_field_series(self):
        if self._field_series:
            return self._field_series.upper()
        else:
            return None

    def _set_field_series(self, series):
        if self._field_series:
            raise Exception("field series already set.")
        if series:
            self._field_series = series.strip().upper()

    field_series = property(_get_field_series, _set_field_series)

    def _get_field_number(self):
        return self._field_number

    def _set_field_number(self, number):
        if self._field_number:
            raise Exception("field number already set.")
        if number:
            self._field_number = int(number)

    field_number = property(_get_field_number, _set_field_number)

    def _get_field_id(self):
        if self._field_series and self._field_number:
            return " ".join([self.field_series, str(self.field_number)])
        elif self._field_series:
            return self.field_series
        elif self._field_number:
            return str(self.field_number)
        else:
            return None

    field_id = property(_get_field_id)

    def _get_seq_label(self):
        series = ''
        for s, l in self.field_series_label_conversions:
            series = series.replace(s, l)
        num = ''
        if self._field_number:
            num = self._field_number
        return '{0}_{1}'.format(series, num)
    
    seq_label = property(_get_seq_label)

    def get_field_id_from_seq_label(seq_label):
        elements = seq_label.strip().split('_')
        if len(elements) < 2:
            raise Exception("invalid seq label {0}".format(seq_label))
        series = elements[0]
        for s, l in self.field_series_label_conversions:
            series = series.replace(l, s)
        num = elements[1]
        return '{0} {1}'.format(series, num).strip()

    def _get_catalog_series(self):
        if self._catalog_series:
            return self._catalog_series.upper()
        else:
            return None

    def _set_catalog_series(self, series):
        if self._catalog_series:
            raise Exception("catalog series already set.")
        if series:
            self._catalog_series = series.strip().upper()

    catalog_series = property(_get_catalog_series, _set_catalog_series)

    def _get_catalog_number(self):
        return self._catalog_number

    def _set_catalog_number(self, number):
        if self._catalog_number:
            raise Exception("catalog number already set.")
        if number:
            self._catalog_number = int(number)

    catalog_number = property(_get_catalog_number, _set_catalog_number)

    def _get_catalog_id(self):
        if self._catalog_series and self._catalog_number:
            return " ".join([self.catalog_series, str(self.catalog_number)])
        elif self._catalog_series:
            return self.catalog_series
        elif self._catalog_number:
            return str(self.catalog_number)
        else:
            return None

    catalog_id = property(_get_catalog_id)

    def _get_genus(self):
        if self._genus:
            return "/".join(sorted(self._genus))
        else:
            return None

    def _set_genus(self, genus):
        if genus:
            if self._genus:
                self._genus.add(genus.strip().capitalize())
            else:
                self._genus = set([genus.strip().capitalize()])

    def _del_genus(self):
        self._genus = None

    genus = property(_get_genus, _set_genus, _del_genus)

    def _get_epithet(self):
        if self._epithet:
            return "/".join(sorted(self._epithet))
        else:
            return None

    def _set_epithet(self, epithet):
        if epithet:
            e = epithet.lower().strip()
            if self._epithet:
                included = False
                for ep in self._epithet:
                    if ep.lower().replace(' ', '').replace('.', '') ==  e.replace(' ', '').replace('.', ''):
                        included = True
                if not included:
                    self._epithet.add(epithet.lower())
            else:
                self._epithet = set([epithet.lower()])

    def _del_epithet(self):
        self._epithet = None

    epithet = property(_get_epithet, _set_epithet, _del_epithet)

    def _get_species(self):
        if self._genus and self._epithet:
            return " ".join([self.genus, self.epithet])
        elif self._genus:
            return self.genus
        elif self._epithet:
            return self.epithet
        else:
            return None

    species = property(_get_species)

    def _get_country(self):
        if self._country:
            return "/".join(sorted(self._country))
        else:
            return None

    def _set_country(self, country):
        if country:
            if self._country:
                self._country.add(country.strip().title())
            else:
                self._country = set([country.strip().title()])

    def _del_country(self):
        self._country = None

    country = property(_get_country, _set_country, _del_country)

    def _get_island(self):
        if self._island:
            return "/".join(sorted(self._island))
        else:
            return None

    def _set_island(self, island):
        if island:
            i = island.lower().replace('.', '').strip().replace('island', '').replace(' isl', '').replace(' is', '').strip()
            if self._island:
                included = False
                for isl in self._island:
                    if isl.lower().replace(' ', '') == i.replace(' ', ''):
                        included = True
                if not included:
                    self._island.add(i.title())
            else:
                self._island = set([i.title()])

    def _del_island(self):
        self._island = None

    island = property(_get_island, _set_island, _del_island)

    def _get_paic(self):
        if self._paic:
            return "/".join(sorted(self._paic))
        else:
            return None

    def _set_paic(self, paic):
        if paic:
            p = paic.lower().strip().replace('paic', '').strip()
            if self._paic:
                included = False
                for pc in self._paic:
                    if pc.lower().replace(' ', '') == p.replace(' ', ''):
                        included = True
                if not included:
                    self._paic.add(p.title())
            else:
                self._paic = set([p.title()])

    def _del_paic(self):
        self._paic = None

    paic = property(_get_paic, _set_paic, _del_paic)

    def _get_locality(self):
        if self._locality:
            return "/".join(sorted(self._locality))
        else:
            return None

    def _set_locality(self, locality):
        if locality:
            l = locality.strip()
            if self._locality:
                included = False
                for loc in self._locality:
                    if loc.lower().replace(' ', '') == l.replace(' ', ''):
                        included = True
                if not included:
                    self._locality.add(l)
            else:
                self._locality = set([l])

    def _del_locality(self):
        self._locality = None

    locality = property(_get_locality, _set_locality, _del_locality)

    def _get_lat(self):
        if self._lat:
            return self._lat
        else:
            return None

    def _set_lat(self, lat):
        if self._lat:
            raise Exception("latitude already set.")
        if isinstance(lat, str):
            l = lat.strip().replace('_', '').strip()
            self._lat = l.strip()
        if isinstance(lat, float):
            self._lat = str(lat)

    lat = property(_get_lat, _set_lat)

    def _get_long(self):
        if self._long:
            return self._long
        else:
            return None

    def _set_long(self, long):
        if self._long:
            raise Exception("longitude already set.")
        if isinstance(long, str):
            l = long.strip().replace('_', '').strip()
            self._long = l.strip()
        if isinstance(long, float):
            self._long = str(long)
            
    long = property(_get_long, _set_long)

    def _get_cam_extract_cell(self):
        if self._cam_extract_cell:
            return "/".join(sorted(self._cam_extract_cell))
        else:
            return None

    def _set_cam_extract_cell(self, cam_extract_cell):
        if cam_extract_cell:
            if self._cam_extract_cell:
                self._cam_extract_cell.add(cam_extract_cell.strip().upper())
            else:
                self._cam_extract_cell = set([cam_extract_cell.strip().upper()])
                self.cam_extract = True

    def _del_cam_extract_cell(self):
        self._cam_extract_cell = None
        self.cam_extract = False

    cam_extract_cell = property(_get_cam_extract_cell, _set_cam_extract_cell, _del_cam_extract_cell)

    def _get_tower(self):
        if self._tower:
            return "/".join(sorted(self._tower))
        else:
            return None

    def _set_tower(self, tower):
        if tower:
            if self._tower:
                self._tower.add(tower.strip().upper())
            else:
                self._tower = set([tower.strip().upper()])

    def _del_tower(self):
        self._tower = None

    tower = property(_get_tower, _set_tower, _del_tower)

    def _get_box(self):
        if self._box:
            return "/".join(sorted(self._box))
        else:
            return None

    def _set_box(self, box):
        if box:
            if self._box:
                self._box.add(box.strip().upper())
            else:
                self._box = set([box.strip().upper()])

    def _del_box(self):
        self._box = None

    box = property(_get_box, _set_box, _del_box)

    def _get_cell(self):
        if self._cell:
            return "/".join(sorted(self._cell))
        else:
            return None

    def _set_cell(self, cell):
        if cell:
            if self._cell:
                self._cell.add(cell.strip().upper())
            else:
                self._cell = set([cell.strip().upper()])

    def _del_cell(self):
        self._cell = None

    cell = property(_get_cell, _set_cell, _del_cell)

    def _get_tissue(self):
        if self._tower or self._box or self._cell:
            return "-".join([str(self.tower), str(self.box), str(self.cell)])
        else:
            return None

    tissue = property(_get_tissue)

    def _get_source(self):
        if self._source:
            return "/".join(sorted(self._source))
        else:
            return None

    def _set_source(self, source):
        if source:
            if self._source:
                self._source.add(source)
            else:
                self._source = set([source])

    source = property(_get_source, _set_source)

    def _get_day(self):
        if self._day:
            return self._day
        else:
            return None

    def _set_day(self, day):
        if self._day:
            raise Exception("collection day already set.")
        if day:
            if isinstance(day, str):
                d = day.strip()
                if d == '' or d == '--' or d == '__' or d == '00':
                    self._day = None
                else:
                    m = self.day_pattern.match(d)
                    if not m:
                        raise ValueError("'%s' is not a valid day." % str(day))
                    self._day = int(m.groups()[0])
            elif isinstance(day, int):
                self._day = day
            else:
                raise ValueError("'%s' is not a valid day." % str(day))
            if self._day and ((self._day > 31) or (self._day < 0)):
                raise ValueError("'%s' is not a valid day." % str(day))

    day = property(_get_day, _set_day)

    def _get_day_str(self):
        if not self._day:
            return ''
        else:
            return "%02d" % self._day

    day_str = property(_get_day_str)

    def _get_month(self):
        if self._month:
            return self._month
        else:
            return None

    def _set_month(self, month):
        if self._month:
            raise Exception("collection month already set.")
        if month:
            if isinstance(month, str):
                mnth = month.strip()
                if mnth == '' or \
                        mnth == '--' or \
                        mnth == '---' or \
                        mnth == '__' or \
                        mnth == '___' or \
                        mnth == '00' or \
                        mnth == '000':
                    self._month = None
                else:
                    md = self.month_digit_pattern.match(mnth)
                    ml = self.month_letter_pattern.match(mnth)
                    if md:
                        self._month = int(md.groups()[0])
                    elif ml:
                        self._month = self.months[ml.groups()[0].lower()]
                    else:
                        raise ValueError("'%s' is not a valid month." % \
                                str(month))
            elif isinstance(month, int):
                self._month = month
            else:
                raise ValueError("'%s' is not a valid month." % str(month))
            if self._month and ((self._month > 12) or (self._month < 1)):
                raise ValueError("'%s' is not a valid month." % str(month))

    month = property(_get_month, _set_month)

    def _get_month_str(self):
        if not self._month:
            return ''
        else:
            return "%02d" % self._month

    month_str = property(_get_month_str)

    def _get_year(self):
        if self._year:
            return self._year
        else:
            return None

    def _set_year(self, year):
        if self._year:
            raise Exception("collection year already set.")
        if year:
            if isinstance(year, str):
                y = year.strip()
                if y == '' or y == '----' or y == '____' or y == '0000':
                    self._year = None
                else:
                    m = self.year_pattern.match(y)
                    if not m:
                        raise ValueError("'%s' is not a valid year." % \
                                str(year))
                    self._year = int(m.groups()[0])
            elif isinstance(year, int):
                self._year = year
            else:
                raise ValueError("'%s' is not a valid year." % str(year))
            if self._year and ((self._year > datetime.datetime.now().year) or \
                    (self._year < 1900)):
                raise ValueError("'%s' is not a valid year." % str(year))

    year = property(_get_year, _set_year)

    def _get_year_str(self):
        if not self._year:
            return ''
        else:
            return "%04d" % self._year

    year_str = property(_get_year_str)

    def _get_date_str(self):
        if (not self._year) and (not self._month) and (not self._day):
            return ''
        if not self._year:
            y = '0000'
        else:
            y = self.year_str
        if not self._month:
            m = '00'
        else:
            m = self.month_str
        if not self._day:
            d = '00'
        else:
            d = self.day_str
        return "-".join([y, m, d])

    date = property(_get_date_str)
