# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

from __future__ import annotations

import os
import logging


def basic(file: str = './log.log') -> None:
    abspath = os.path.abspath(file)
    dirname = os.path.dirname(abspath)
    os.makedirs(dirname, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s |%(levelname)s| |[%(filename)s:%(lineno)d][%(funcName)s]| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=abspath,
        filemode='w')
    logging.info(f'file     : {file}')
    logging.info(f'abspath  : {abspath}')
    logging.info(f'dirname  : {dirname}')
