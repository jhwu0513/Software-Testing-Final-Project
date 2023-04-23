import grpc
import voting_pb2
import voting_pb2_grpc
import os
import base64

from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
from datetime import timedelta
from concurrent import futures
from nacl.signing import VerifyKey
from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey

Voter_dict = {} 
'''
Voter is a Dictionary 
index : Voter Name
Value : A tuple (group,public_key)
eg. {"Bob":("students","ajdalkwjljfjfef")}
'''

class LocalService:
    def __init__(self):
        return
    def RegisterVoter(self, voter):
        print("RegisterVoter API Called:")
        print(voter)
        try:
            if voter.name not in Voter_dict:
                Voter_dict[voter.name] = (voter.group,voter.public_key)
                status = voting_pb2.Status()
                status.code = 0
            elif voter.name in Voter_dict:
                status = voting_pb2.Status()
                status.code = 1
        except Exception as e:
            # undefined error
            status = voting_pb2.Status()
            status.code = 2
        return status
    def UnregisterVoter(self, voter_name):
        print("UnregisterVoter API Called:")
        print(voter_name)
        try:
            if voter_name.name in Voter_dict:
                del Voter_dict[voter_name.name]
                status = voting_pb2.Status()
                status.code = 0
            elif voter_name.name not in Voter_dict:
                status = voting_pb2.Status()
                status.code = 1
        except Exception as e:
            # undefined error
            status = voting_pb2.Status()
            status.code = 2
        return status

class eVotingServicer(voting_pb2_grpc.eVotingServicer):
    def __init__(self):
        '''
        - key: Election.name
        - value: {Election.choices:votes,"group":Election.groups,"voted":[AuthToken.value base64 encoded],"endate":Election.end_date}
        '''
        self.election = {}
        '''
        - key: AuthToken.value base64 encoded: Base64Encoder.encode(os.urandom(64))
        - value: [Voter.name, expired_time: Timestamp,Voter.group]
        '''
        self.auth_tokens = {}

    def VerifyAuthToken(self, auth_token):
        current_date = Timestamp()
        current_date.GetCurrentTime()
        b64_auth_token = Base64Encoder.encode(auth_token)
        print(b64_auth_token)
        if b64_auth_token not in list(self.auth_tokens.keys()):
            print(f"Please PreAuth First.")
            return False
        else:
            name, expired_time, group = self.auth_tokens[b64_auth_token]
            if current_date.seconds >= expired_time:
                print(f"Given Auth Token Is Expired. Please PreAuth Again.")
                return False
            else:
                print(f"Valid Auth Token. Update Stored Auth Token Expired Time")
                del self.auth_tokens[b64_auth_token]
                self.auth_tokens[b64_auth_token] = [name, current_date.seconds + 3600, group]
        return True

    def PreAuth(self, request, context):
        print("PreAuth Request Made:")
        print(request)
        preAuth_reponse = voting_pb2.Challenge()
        preAuth_reponse.value = b'Challenge'
        return preAuth_reponse

    def Auth(self, request, context):
        print("Auth Request Made:")
        print(request)

        auth_reponse = voting_pb2.AuthToken()
        name = request.name.name
        signature = request.response.value

        try:
            public_key = Voter_dict[name][1]
            VerifyKey(public_key).verify(b"Challenge", signature)
            print(f"{name}'s Signature Validity Checked.")

            for key in self.auth_tokens.keys():
                if self.auth_tokens[key][0] == name:
                    del self.auth_tokens[key]
                    break

            auth_reponse.value = os.urandom(64)
            current_date = Timestamp()
            current_date.GetCurrentTime()
            current_date.seconds += 3600
            self.auth_tokens[Base64Encoder.encode(auth_reponse.value)] = [name, current_date.seconds,Voter_dict[name][0]]
            print(f"Current Stored Auth Token: {self.auth_tokens}")

        except Exception as e: 
            print(e)
            auth_reponse.value = e.__repr__().encode()

        return auth_reponse

    def CreateElection(self, request, context):
        createElection_reponse = voting_pb2.Status()
        try:
            # invalid auth
            if(not self.VerifyAuthToken(request.token.value)):
                createElection_reponse.code = 1
                return createElection_reponse
            # missing groups or choices
            if len(request.groups) < 1 or len(request.choices) < 1:
                createElection_reponse.code = 2
                return createElection_reponse
            if request.name not in self.election.keys():
                self.election[request.name] = {}
                self.election[request.name]["group"] = list(request.groups)
                self.election[request.name]["voted"] = []
                self.election[request.name]["endate"] = request.end_date
                for choice in request.choices:
                    self.election[request.name][choice] = 0
            createElection_reponse.code = 0
            return createElection_reponse
        except Exception as e:
            # unknown error
            createElection_reponse.code = 3
            print(e)
            return createElection_reponse

    def CastVote(self, request, context):
        castVote_reponse = voting_pb2.Status()
        # invalid auth
        if(not self.VerifyAuthToken(request.token.value)):
            castVote_reponse.code = 1
            return castVote_reponse
        # invalid election name
        if request.election_name not in self.election.keys():
            castVote_reponse.code = 2
            return castVote_reponse
        # the voter's group is not allowed in the election
        if self.auth_tokens[Base64Encoder.encode(request.token.value)][-1] not in self.election[request.election_name]["group"]:
            castVote_reponse.code = 3
            return castVote_reponse
        # a previous vote has been election
        if Base64Encoder.encode(request.token.value) in self.election[request.election_name]["voted"]:
            castVote_reponse.code = 4
            return castVote_reponse
        # valid casting
        self.election[request.election_name][request.choice_name] += 1
        self.election[request.election_name]["voted"].append(Base64Encoder.encode(request.token.value))
        castVote_reponse.code = 0
        return castVote_reponse
    
    def GetResult(self, request, context):
        getResult_reponse = voting_pb2.ElectionResult()
        # non-exist election
        if request.name not in self.election.keys():
            getResult_reponse.status = 1
            return getResult_reponse
        # ongoing election
        current = Timestamp()
        current.GetCurrentTime()
        # 28,800 -> UTF+8
        if (datetime.fromtimestamp(current.ToSeconds())+timedelta(seconds=28800)) <= datetime.fromtimestamp(self.election[request.name]["endate"].ToSeconds()):
            getResult_reponse.status = 2
            return getResult_reponse
        # valid query
        for choice,count in self.election[request.name].items():
            if choice in ["group","voted","endate"]:
                continue
            getResult_reponse.counts.extend([voting_pb2.VoteCount(choice_name= choice, count= count)])
        getResult_reponse.status = 0
        print(getResult_reponse)
        return getResult_reponse

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    voting_pb2_grpc.add_eVotingServicer_to_server(eVotingServicer(), server)
    local_api = LocalService()
    
    while True:
        print("1. RegisterVoter")
        print("2. UnregisterVoter")
        print("3. List Voter ")
        print("4. Leave registration ")
        api_call = input("Which Local Server API would you like to make ? ")
        if api_call == "1":
            with open('voter.txt') as f:
                lines = f.readlines()
                for i in range(len(lines)):
                    data = lines[i].split(' ')
                    name = data[0]
                    group = data[1]
                    seed = base64.b64decode(data[2])
                    sk = SigningKey(seed)
                    public_key = sk.verify_key._key
                    voter = voting_pb2.Voter()
                    voter.name = name
                    voter.group = group
                    voter.public_key = public_key
                    status = local_api.RegisterVoter(voter)
                    print("Status : ",status)
        elif api_call == "2":
            name = input("voter name: ")
            voter = voting_pb2.VoterName()
            voter.name = name
            status = local_api.UnregisterVoter(voter)
            print("Status : ",status)
        elif api_call == "3":
            for x in Voter_dict:
                print (x,':',Voter_dict[x])
        elif api_call == "4":
            break
        else:
            print("Invalid input.\n")
            exit(1)
        print()

    address = input("Server address (127.0.0.1): ")
    if not address: address = "127.0.0.1"

    port = input("Service port (50000): ")
    if not port: port = 50000
    
    server.add_insecure_port(f"{address}:{port}")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()