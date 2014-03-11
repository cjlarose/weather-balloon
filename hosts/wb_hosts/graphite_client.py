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
        #logger.debug(r.json())
        return r.json()

    def _merge_metrics(self, targets, prefix=""):
        """
        Graphite returns something of the form [{target: "cpu.idle", datapoints: [[value, time]]}].
        This function yields instead [{time: time, cpu.idle: value, cpu.waiting: value2}].
        Implementation is naive. Optimization may be necessary.
        """
        r = {}
        for target in targets:
            target_name = target['target'].replace(prefix, "", 1)
            for value, time in target['datapoints']:
                if value is not None:
                    if not r.has_key(time):
                        r[time] = {'time': time}
                    r[time][target_name] = value

        sorted_values = sorted(r.values(), key=itemgetter('time'))
        return sorted_values

    def get_stats(self, client_name, query='*.*', params={}):
        prefix = "stats.%s." % client_name
        target = prefix + query
        metrics = self._get_json(target, params)
        return self._merge_metrics(metrics, prefix)
        
    def get_cpu_stats(self, client_name, params={}):
        return self.get_stats(client_name, 'cpu.*', params)

    def get_memory_stats(self, client_name, params={}):
        return self.get_stats(client_name, 'memory.*', params)
