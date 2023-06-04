import afl
import os
import sys
sys.path.append(r"../Test-Target")
import voting_pb2_grpc
import voting_pb2
import grpc
import voting_server
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

from nacl.signing import SigningKey

afl.init()

address = "127.0.0.1"
port = 50000

# pid = os.fork()
# if pid == 0:

with open(0, 'rb') as f:

    channel = grpc.insecure_channel(f'{address}:{port}')
    stub = voting_pb2_grpc.eVotingStub(channel)
    
    #PreAuth
    preAuth_request = voting_pb2.VoterName(name = f.read())
    preAuth_response = stub.PreAuth(preAuth_request)
    assert(preAuth_response.value == b'Challenge')

os._exit(0)