import voting_pb2_grpc
import voting_pb2
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

from nacl.signing import SigningKey

def run(address, port, auth_token):
    with grpc.insecure_channel(f'{address}:{port}') as channel:
        stub = voting_pb2_grpc.eVotingStub(channel)
        print("1. PreAuth")
        print("2. CreateElection")
        print("3. CastVote")
        print("4. GetResult")
        print("q. exit.")
        rpc_call = input("Which RPC would you like to make ? ")

        if rpc_call == "1":
            name = input("voter name: ")
            preAuth_request = voting_pb2.VoterName(name = name)
            preAuth_response = stub.PreAuth(preAuth_request)
            challenge = preAuth_response.value

            # generate ed25519 key pair
            # sk = SigningKey.generate()
            # seed = sk._seed

            # use imported seed
            seed = b'\xa8\xce\x88\xf0}\xed4\x850\xa6&s\xc2\xd1\x81\x8f\xbe\xfd\xae>BO\xb1$\xec\xe2O\xca\xc6k\x08D'
            sk = SigningKey(seed)
            private_key = sk._signing_key
            public_key = sk.verify_key._key
            print(f"seed: {seed}\nprivate key: {private_key}\npublic key: {public_key}")

            signature = SigningKey(seed).sign(challenge).signature
            print(f"detached signature: {signature}")
            
            # forged signature test
            # signature = signature[:-1] + bytes([int(signature[-1]) ^ 1])

            auth_request = voting_pb2.AuthRequest(
                name = voting_pb2.VoterName(name = name), 
                response = voting_pb2.Response(value = signature))
            auth_token = stub.Auth(auth_request).value

            print(f"{name}'s Auth Result: {auth_token}")

        elif rpc_call == "2":
            dt = datetime.fromisoformat(input("end date (e.g., 2023-01-01T00:00:00): "))
            end_date = Timestamp()
            end_date.FromDatetime(dt)
            createElection_request = voting_pb2.Election(
                name = input("election name: "), 
                groups = input("groups (sep by ','): ").split(','),
                choices = input("choices (sep by ','): ").split(','),
                end_date = end_date,
                token = voting_pb2.AuthToken(value= auth_token)
            )
            createElection_response = stub.CreateElection(createElection_request)
            print(f"CreateElection Response Received. {createElection_response}")
        elif rpc_call == "3":
            castVote_request = voting_pb2.Vote(
                election_name = input("election name: "), 
                choice_name = input("choice name: "),
                token = voting_pb2.AuthToken(value= auth_token)
            )
            castVote_response = stub.CastVote(castVote_request)
            print(f"CastVote Response Received. {castVote_response}")
        elif rpc_call == "4":
            getResult_request = voting_pb2.ElectionName(
                name = input("election name: "), 
            )
            getResult_response = stub.GetResult(getResult_request)
            print(f"GetResult Response Received. {getResult_response}")
        elif rpc_call == 'q' or 'Q': 
            print("Bye !\n")
            exit(0)
        else: 
            print("Invalid input.\n")
            exit(1)
        
        return auth_token

if __name__ == "__main__":
    address = input("Server address (127.0.0.1): ")
    if not address: address = "127.0.0.1"

    port = input("Service port (50000): ")
    if not port: port = 50000

    auth_token = b''
    while 1:
        auth_token = run(address, port, auth_token)