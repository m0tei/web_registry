# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import hashlib
import binascii
from datetime import datetime

# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/


def hash_pass(password):
    """Hash a password for storing."""

    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash)  # return bytes


def verify_pass(provided_password, stored_password):
    """Verify a stored password against one provided by user"""

    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

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
    print(formatted_date)

    return formatted_date
