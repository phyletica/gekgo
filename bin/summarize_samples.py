#! /usr/bin/env python

import os
import sys
import logging
import re
import csv

import gekgo_util
from gekgo_util import RunLogger

_LOG = RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

def get_row_value_dict(dict_reader, header_str):
    row_dict = {}
    for row in dict_reader:
            
def get_dict_reader(file_stream, delimiter='\t'):
    return csv.DictReader(file_stream, delimiter=delimiter)

