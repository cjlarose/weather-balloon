from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from wb_services.hosts import Hosts
from wb_services.hosts.ttypes import Host

class HostsService(object):
    def __init__(self, host, port):
        socket = TSocket.TSocket(host, port)
        transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = Hosts.Client(protocol)
        transport.open()

    def set_hosts(self, hosts):
        return self.client.set_hosts([Host(**h) for h in hosts])
