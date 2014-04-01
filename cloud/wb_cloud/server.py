import sys
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from wb_cloud.settings import config
from wb_services.hosts import Hosts
from wb_cloud.handler import Handler

if __name__ == "__main__":
    port = 8000

    engine = create_engine(config['db_url'])
    Session = sessionmaker(bind=engine)
    handler = Handler(Session())

    processor = Hosts.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print "Starting python server..."
    server.serve()
    print "done!"
