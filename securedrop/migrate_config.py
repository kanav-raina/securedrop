#!/usr/bin/env python

from __future__ import print_function

import json
import os
import sys

from argparse import ArgumentParser
from os import path


CONFIG_FILE = '/etc/securedrop/config.json'
TMP_CONFIG_FILE = '/etc/securedrop/config.json.tmp'


def main(force):
    try:
        import config  # noqa
        HAS_CONFIG = True
        print('Python config imported')
    except ImportError:
        HAS_CONFIG = False
        print('Python config unable to be imported')

    if path.exists(CONFIG_FILE):
        if force:
            print('JSON config already exists, but --force was specified. '
                  'Overwriting config.')
        else:
            print('JSON config already exists. Exiting')
            sys.exit(0)
    else:
        if not HAS_CONFIG:
            print('Python config file missing, unable to migrate',
                  file=sys.stderr)
            sys.exit(1)

    id_pepper = config.SCRYPT_ID_PEPPER
    gpg_pepper = config.SCRYPT_GPG_PEPPER

    try:
        default_locale = config.DEFAULT_LOCALE
    except AttributeError:
        default_locale = 'en_US'

    try:
        supported_locales = config.SUPPORTED_LOCALES
    except AttributeError:
        supported_locales = ['en_US']

    i18n = {
        'default_locale': default_locale,
        'supported_locales': supported_locales,
    }

    out = {
        'source_interface': {
            'secret_key': config.SourceInterfaceFlaskConfig.SECRET_KEY,
            'scrypt_id_pepper': id_pepper,
            'scrypt_gpg_pepper': gpg_pepper,
            'i18n': i18n,
        },
        'journalist_interface': {
            'secret_key': config.JournalistInterfaceFlaskConfig.SECRET_KEY,
            'scrypt_id_pepper': id_pepper,
            'scrypt_gpg_pepper': gpg_pepper,
            'i18n': i18n,
        },
    }

    # using temp file to not clobber original in the event of an IO error
    with open(TMP_CONFIG_FILE, 'w') as f:
        f.write(json.dumps(out))

    os.rename(TMP_CONFIG_FILE, CONFIG_FILE)

    try:
        os.remove(TMP_CONFIG_FILE)
    except OSError:
        pass


if __name__ == '__main__':
    parser = ArgumentParser(
        path.basename(__file__),
        description='Helper for migrating config from Python to JSON')
    parser.add_argument('--force', action='store_true',
                        help='Overwrite the existing config.json')
    args = parser.parse_args()

    main(force=args.force)
