import re
import requests
import logging

logger = logging.getLogger(__file__)

#TODO first section(123) works, 2nd section doesnt
#              12    3        4     5   6
url_pattern = r'^(http(s)?://)?(\w*\.)*\w*\.\w*'
url_comp = re.compile(url_pattern)
#1 start of string
#2 http:// maybe
#3 maybe s in https
#4 0 to many subdomains
#5 a single domain
#6 top level domain


#validate url is in right form
def validate_url_format(url):
    if url_comp.match(url) is None:
        return False
    return True


def validate_url_alive(url):
    resp = None
    try:
        resp = requests.get(url)
    except:
        return False
    if resp is not None and resp.status_code >= 200 and resp.status_code < 400:
        return True

def validate_url(url):
    logger.debug("in validate url for url: " + url)
    #does it even matter what the form is if it gives a 200/300 response?
    """
    if not validate_url_format(url):
        logger.debug("not a valid format, returning")
        return False
    """

    if not validate_url_alive(url):
        logger.debug("not alive, returning")
        return False

    logger.debug("looks like a valid url")
    return True

#TODO fill this shit out more lol
#TODO url canonicalization
#TODO define cannonicalized url format
