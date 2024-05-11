# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import hashlib
import binascii
from datetime import datetime

# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/

def format_date(input_date):
    # Parse the input date string
    parsed_date = datetime.strptime(input_date, '%Y-%m-%d')

    # Format the parsed date to desired format
    formatted_date = parsed_date.strftime('%m/%d/%Y')
    return formatted_date

def format_reverse_date(input_date):
    # Parse the input date string
    parsed_date = datetime.strptime(input_date, '%d/%m/%Y')

    # Format the parsed date to the reverse format
    formatted_date = parsed_date.strftime('%Y-%m-%d')

    return formatted_date
