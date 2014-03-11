import requests
import logging
from operator import itemgetter

logger = logging.getLogger(__name__)

class Graphite(object):
    def __init__(self, host):
        self.endpoint = host + "/render"

    def _get_json(self, target, params={}):
        payload = {
            'target': target,
            'format': 'json',
        }
        payload.update(params)
        logger.debug(payload)
        r = requests.get(self.endpoint, params=payload)
        r.raise_for_status()
        return r.json()

    def get_stats(self, client_name, query='*.*', params={}):
        prefix = "nagios.%s." % client_name
        target = prefix + query
        metrics = self._get_json(target, params)
        for m in metrics:
            m[u'target'] = m[u'target'].replace(prefix, "", 1)
        return metrics
