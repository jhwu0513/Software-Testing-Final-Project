import afl
import os
import sys
sys.path.append(r"../../Test-Target")
import voting_pb2_grpc
import voting_pb2
import grpc
import voting_server
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

from nacl.signing import SigningKey

afl.init()

with open(0, 'r') as f:
    evs = voting_server.eVotingServicer()
    #PreAuth
    # try:
    challenge = evs.PreAuth(f.read(), None)
    assert(challenge.value == b'Challenge')
    # except UnicodeDecodeError:
    #     pass

os._exit(0)