#!/bin/env python3

import argparse
import imp
import logging
import sys
import os

import watcher
import config


def main(argv):
    parser = argparse.ArgumentParser('mail_notify')
    parser.add_argument('maildir')
    parser.add_argument('--config', '-c', help="configuration file")
    parser.add_argument('--verbose', '-v', help="make me verbose", action='store_true')
    parser.add_argument('--debug', help="make me very verbose", action='store_true')
    args = parser.parse_args(argv)

    logger_level = logging.WARNING
    logger_format = '%(levelname)s: %(message)s'
    if args.verbose:
        logger_level = logging.INFO
    if args.debug:
        logger_level = logging.NOTSET
        logger_format = '%(asctime)-15s: %(name)s: %(levelname)s: %(message)s'
    logging.basicConfig(format=logger_format, level=logger_level)

    basedir = os.path.dirname(__file__)
    config.override(imp.load_source('config', os.path.join(basedir, 'default_config')).__dict__)
    if args.config:
        config.override(imp.load_source('config', args.config).__dict__)

    config.override(args.__dict__)

    watcher.watch_maildir(args.maildir)


if __name__ == '__main__':
    main(sys.argv[1:])
