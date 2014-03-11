from pynag.Model import Host
from pynag.Control.Command import send_command

from wb_services.hosts import Hosts

ATMO_HOSTGROUP_NAME = 'atmo-vms'
ATMO_HOST_TEMPLATE = 'atmo_vm'
ATMO_HOST_FILE = '/etc/nagios/atmo-hosts.cfg'

class Handler(Hosts.Iface):

    def __init__(self, graphite):
        self.graphite = graphite

    @staticmethod
    def to_pynag_host(host):
        new_host = Host()
        new_host.host_name = host.id
        new_host.alias = new_host.display_name = host.display_name
        new_host.address = host.address
        new_host.hostgroups = ATMO_HOSTGROUP_NAME
        new_host.use = ATMO_HOST_TEMPLATE
        new_host.set_filename(ATMO_HOST_FILE)
        return new_host

    def set_hosts(self, hosts):
        """
        Write Nagios config file; restart daemon
        """
        # Remove All monitored hosts
        for host in Host.objects.filter(hostgroups=ATMO_HOSTGROUP_NAME):
            host.delete()

        # Add all passed-in hosts
        for host in [Handler.to_pynag_host(h) for h in hosts]:
            host.save()

        # Restart the nagios daemon
        send_command("RESTART_PROGRAM")

    def get_metrics(self, host_name, key):
        """
        Query graphite for metrics
        """
        pass
