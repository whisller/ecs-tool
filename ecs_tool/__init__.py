import logging

import click_log

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
click_log.basic_config(logger)
