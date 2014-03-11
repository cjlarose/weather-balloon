import sys
import os

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from wb_services.hosts import Hosts
from wb_hosts.handler import Handler
from wb_hosts.graphite_client import Graphite

if __name__ == "__main__":
    port = 8000

    graphite = Graphite(os.environ['GRAPHITE_PORT_8080_TCP_ADDR'] +
        ":" + os.environ['GRAPHITE_PORT_8080_TCP_PORT'])
    handler = Handler(graphite)
    processor = Hosts.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print "Starting python server..."
    server.serve()
    print "done!"
