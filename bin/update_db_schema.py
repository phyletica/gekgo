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

def update_database_schema(sample_db):
    return sample_db.get_copy()

def main():
    db = SampleDatabase(path=gekgo_util.DB_PATH)
    new_db = update_database_schema(db)
    new_db.path = gekgo_util.DB_PATH
    new_db.commit()

if __name__ == '__main__':
    main()
