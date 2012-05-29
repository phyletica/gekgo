#! /usr/bin/env python

import os
import sys
import logging
import re
import datetime

import gekgo_util
from gekgo_util import RunLogger

_LOG = RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

class GekkonidSamples(dict):
    """
    A dictionary of Gekkonid Sample instances.
    """
    def __init__(self):
        dict.__init__()
        self._species_set = set()
        self._update_species_set()

    def _update_species_set(self):
        self._species_set = set()
        for sample in self.itervalues():
            self._species_set.add(sample.species)

    def _get_species_set(self):
        self._update_species_set()
        return self._species_set

    species = property(_get_species_set)

    def add(sample_object):
        if not isintance(sample_object, Sample):
            raise Exception("GekkonidSamples dict only holds Sample objects.")
        if not sample_object.field_id:
            raise Exception("Sample does not have field id; cannot add.")
        if sample_object.field_id in self.keys():
            _LOG.warning(
                    "'%s' already in dict; updating this sample" % \
                    sample_object.field_id)
            self[sample_object.field_id].update(sample_object)
            self._species_set.add(self[sample_object.field_id].species)
        else:
            self[sample_object.field_id] = sample_object
            self._species_set.add(self[sample_object.field_id].species)

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

    def __init__(self, **kwargs):
        self._field_series = None
        self._field_number = None
        self._catalog_series = None
        self._catalog_number = None
        self._genus = None
        self._epithet = None
        self._island = None
        self._extract_cell = None
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
        self.island = kwargs.pop('island', None)
        self.extract_cell = kwargs.pop('extract_cell', None)
        self.extract = kwargs.pop('extract', False)
        if self.extract_cell:
            self.extract = True
        self.day = kwargs.pop('day', None)
        self.month = kwargs.pop('month', None)
        self.year = kwargs.pop('year', None)
        self.source = kwargs.pop('source', None)
        if len(kwargs.keys()) > 0:
            _LOG.warning("Unused kwargs passed to Sample.__init__ for '%s':\n" % \
                          self.field_id + \
                      "\t%s" % ", ".join([str(x) for x in kwargs.keys()]))

    def update(sample_object):
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
            assert self.catalog_number == sample_object.catalog_number
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
        self.genus = sample_object.genus
        self.epithet = sample_object.epithet
        self.island = sample_object.island
        self.extract_cell = sample_object.extract_cell
        self.source = sample_object.source

    def _get_field_series(self):
        if self._field_series:
            return self._field_series.upper()
        else:
            return None

    def _set_field_series(self, series):
        if self._field_series:
            raise Exception("field series already set.")
        if series:
            self._field_series = series.upper()

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

    def _get_catalog_series(self):
        if self._catalog_series:
            return self._catalog_series.upper()
        else:
            return None

    def _set_catalog_series(self, series):
        if self._catalog_series:
            raise Exception("catalog series already set.")
        if series:
            self._catalog_series = series.upper()

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
            return ",".join(self._genus)
        else:
            return None

    def _set_genus(self, genus):
        if genus:
            if self._genus:
                self._genus.add(genus.capitalize())
            else:
                self._genus = set([genus.capitalize()])

    genus = property(_get_genus, _set_genus)

    def _get_epithet(self):
        if self._epithet:
            return ",".join(self._epithet)
        else:
            return None

    def _set_epithet(self, epithet):
        if epithet:
            if self._epithet:
                self._epithet.add(epithet.lower())
            else:
                self._epithet = set([epithet.lower()])

    epithet = property(_get_epithet, _set_epithet)

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

    def _get_island(self):
        if self._island:
            return ",".join(self._island)
        else:
            return None

    def _set_island(self, island):
        if island:
            if self._island:
                self._island.add(island.capitalize())
            else:
                self._island = set([island.capitalize()])

    island = property(_get_island, _set_island)

    def _get_extract_cell(self):
        if self._extract_cell:
            return ",".join(self._extract_cell)
        else:
            return None

    def _set_extract_cell(self, extract_cell):
        if extract_cell:
            if self._extract_cell:
                self._extract_cell.add(extract_cell.upper())
            else:
                self._extract_cell = set([extract_cell.upper()])
                self.extract = True

    extract_cell = property(_get_extract_cell, _set_extract_cell)

    def _get_source(self):
        if self._source:
            return ",".join(self._source)
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
                m = self.day_pattern.match(day.strip())
                if not m:
                    raise ValueError("'%s' is not a valid day." % str(day))
                self._day = int(m.groups()[0])
            elif isinstance(day, int):
                self._day = day
            else:
                raise ValueError("'%s' is not a valid day." % str(day))
            if (self._day) > 31 or (self._day < 1):
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
                md = self.month_digit_pattern.match(month.strip())
                ml = self.month_letter_pattern.match(month.strip())
                if md:
                    self._month = int(md.groups()[0])
                elif ml:
                    self._month = self.months[ml.groups()[0].lower()]
                else:
                    raise ValueError("'%s' is not a valid month." % str(month))
            elif isinstance(month, int):
                self._month = month
            else:
                raise ValueError("'%s' is not a valid month." % str(month))
            if (self._month > 12) or (self._month < 1):
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
                m = self.year_pattern.match(year.strip())
                if not m:
                    raise ValueError("'%s' is not a valid year." % str(year))
                self._year = int(m.groups()[0])
            elif isinstance(year, int):
                self._year = year
            else:
                raise ValueError("'%s' is not a valid year." % str(year))
            if (self._year > datetime.datetime.now().year) or (self._year < 1900):
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
