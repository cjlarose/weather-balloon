from wb_services.hosts import Hosts

class Handler(Hosts.Iface):
    def __init__(self):
        pass

    def set_hosts(hosts):
        """
        Write Nagios config file; restart daemon
        """
        pass

    def get_metrics(host_name, key):
        """
        Query graphite for metrics
        """
        pass
