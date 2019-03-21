
import logging
import logging.config, yaml

def init(cls):
    logging.config.dictConfig(yaml.load(open('logging.yml', 'r')))
    logger = logging.getLogger("%s" % (cls))
    logger.setLevel(logging.DEBUG)
    return logger

def get(cls):
    logger = logging.getLogger("%s" % (cls))
    logger.setLevel(logging.DEBUG)
    return logger
