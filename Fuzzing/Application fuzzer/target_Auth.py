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

evs = voting_server.eVotingServicer()
with open(0, 'r') as f:
    
    try:
        in_text = f.read().split(" ")
    except UnicodeDecodeError:
        os._exit(0)

    x = in_text[0]
    y = in_text[1]

    assert(y == "Jason")

os._exit(0)