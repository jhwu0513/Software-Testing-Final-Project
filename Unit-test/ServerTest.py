import sys
import unittest
import io
from unittest.mock import Mock,patch,MagicMock
sys.path.append(r"..\Test-Target")
import voting_server
import voting_pb2
from nacl.encoding import Base64Encoder
import voting_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta
from parameterized import parameterized
from nacl.signing import SigningKey

class Test(unittest.TestCase):
    def setUp(self):
        self.evs = voting_server.eVotingServicer()

    def test_VerifyAuthToken_1(self): # 共3種情況
        token = b'token'
        self.assertEqual(self.evs.VerifyAuthToken(token), False)
        token = b'token'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['John', (datetime.now() + timedelta(hours=1)).timestamp(), 'A']
        self.assertEqual(self.evs.VerifyAuthToken(token), True)
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['John', (datetime.now() - timedelta(hours=1)).timestamp(), 'A']
        self.assertEqual(self.evs.VerifyAuthToken(token), False)
        print("test_VerifyAuthToken_1")
    
    def test_VerifyAuthToken_2(self): # 共3種情況
        token = b'Hello'
        self.assertEqual(self.evs.VerifyAuthToken(token), False)
        token = b'Hello'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'B']
        self.assertEqual(self.evs.VerifyAuthToken(token), True)
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() - timedelta(hours=1)).timestamp(), 'B']
        self.assertEqual(self.evs.VerifyAuthToken(token), False)
        print("test_VerifyAuthToken_2")
    
    def test_VerifyAuthToken_3(self): # 共3種情況
        token = b'fajsdgjlndsiesif'
        self.assertEqual(self.evs.VerifyAuthToken(token), False)
        token = b'jekffqlnijklaj3jeawfgbvjhhehgsbdf'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['bbufahci', (datetime.now() + timedelta(hours=1)).timestamp(), 'dhic']
        self.assertEqual(self.evs.VerifyAuthToken(token), True)
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['hauhaohcoa', (datetime.now() - timedelta(hours=1)).timestamp(), 'sjdii']
        self.assertEqual(self.evs.VerifyAuthToken(token), False)
        print("test_VerifyAuthToken_3")
    
    def test_PreAuth(self): # 共10種情況
        test_case = [None, "Bob", "Alice", "123", "4565", "65656854", "55454546", "5546454", "erjorugjl", "kworjfepiwrwrere"] 
        for test in test_case:
            challenge = self.evs.PreAuth(test, None)
            self.assertEqual(challenge.value, b'Challenge')
        print("test_PreAuth")

    @patch('voting_server.grpc.server')
    @patch('voting_server.voting_pb2_grpc.add_eVotingServicer_to_server')
    @patch('builtins.input', side_effect=["1", "127.0.0.1", "50000"])
    def test_Auth_1(self, mock_input, mock_add_servicer, mock_server): # 共2種情況
        request = voting_pb2.AuthRequest(name = voting_pb2.VoterName(name = 'John'), response = voting_pb2.Response(value = b'signature'))
        response = self.evs.Auth(request, None)
        self.assertIsInstance(response.value, bytes)

        mock_server_instance = mock_server.return_value
        mock_server_instance.wait_for_termination = Mock()
        voter_data = "Bob students qM6I8H3tNIUwpiZzwtGBj779rj5CT7Ek7OJPysZrCEQ=\n"
        with patch('builtins.open', return_value=io.StringIO(voter_data)) as mock_file:
            server = voting_server.serve()
            self.assertEqual(server.api_call, "1")
            self.assertEqual(server.address, "127.0.0.1")
            self.assertEqual(server.port, "50000")
            mock_add_servicer.assert_called_once()
            mock_server.assert_called_once()
            mock_server_instance.add_insecure_port.assert_called_once_with("127.0.0.1:50000")
            mock_server_instance.start.assert_called_once()
            mock_server_instance.wait_for_termination.assert_called_once()

            token = b'token'
            self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
            seed = b'\xa8\xce\x88\xf0}\xed4\x850\xa6&s\xc2\xd1\x81\x8f\xbe\xfd\xae>BO\xb1$\xec\xe2O\xca\xc6k\x08D'
            request = voting_pb2.AuthRequest(name = voting_pb2.VoterName(name = 'Bob'), response = voting_pb2.Response(value = SigningKey(seed).sign(b'Challenge').signature))
            response = self.evs.Auth(request, None)
            self.assertIsInstance(response.value, bytes)
        print("test_Auth_1")
    
    @patch('voting_server.grpc.server')
    @patch('voting_server.voting_pb2_grpc.add_eVotingServicer_to_server')
    @patch('builtins.input', side_effect=["1", "127.0.0.1", "50000"])
    def test_Auth_2(self, mock_input, mock_add_servicer, mock_server): # 共2種情況
        request = voting_pb2.AuthRequest(name = voting_pb2.VoterName(name = 'Alice'), response = voting_pb2.Response(value = b'signature'))
        response = self.evs.Auth(request, None)
        self.assertIsInstance(response.value, bytes)

        mock_server_instance = mock_server.return_value
        mock_server_instance.wait_for_termination = Mock()
        voter_data = "Bob students qM6I8H3tNIUwpiZzwtGBj779rj5CT7Ek7OJPysZrCEQ=\n"
        with patch('builtins.open', return_value=io.StringIO(voter_data)) as mock_file:
            server = voting_server.serve()
            self.assertEqual(server.api_call, "1")
            self.assertEqual(server.address, "127.0.0.1")
            self.assertEqual(server.port, "50000")
            mock_add_servicer.assert_called_once()
            mock_server.assert_called_once()
            mock_server_instance.add_insecure_port.assert_called_once_with("127.0.0.1:50000")
            mock_server_instance.start.assert_called_once()
            mock_server_instance.wait_for_termination.assert_called_once()

            token = b'token'
            self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
            seed = b'\xa8\xce\x88\xf0}\xed4\x850\xa6&s\xc2\xd1\x81\x8f\xbe\xfd\xae>BO\xb1$\xec\xe2O\xca\xc6k\x08D'
            request = voting_pb2.AuthRequest(name = voting_pb2.VoterName(name = 'kaksdkoa'), response = voting_pb2.Response(value = SigningKey(seed).sign(b'Challenge').signature))
            response = self.evs.Auth(request, None)
            self.assertIsInstance(response.value, bytes)
        print("test_Auth_2")

    @patch('voting_server.grpc.server')
    @patch('voting_server.voting_pb2_grpc.add_eVotingServicer_to_server')
    @patch('builtins.input', side_effect=["1", "127.0.0.1", "50000"])
    def test_Auth_3(self, mock_input, mock_add_servicer, mock_server): # 共3種情況
        request = voting_pb2.AuthRequest(name = voting_pb2.VoterName(name = 'hiiwjjsaj'), response = voting_pb2.Response(value = b'signature'))
        response = self.evs.Auth(request, None)
        self.assertIsInstance(response.value, bytes)

        request = voting_pb2.AuthRequest(name = voting_pb2.VoterName(name = 'dsjcjdjc6666666'), response = voting_pb2.Response(value = b'signature'))
        response = self.evs.Auth(request, None)
        self.assertIsInstance(response.value, bytes)

        mock_server_instance = mock_server.return_value
        mock_server_instance.wait_for_termination = Mock()
        voter_data = "Bob students qM6I8H3tNIUwpiZzwtGBj779rj5CT7Ek7OJPysZrCEQ=\n"
        with patch('builtins.open', return_value=io.StringIO(voter_data)) as mock_file:
            server = voting_server.serve()
            self.assertEqual(server.api_call, "1")
            self.assertEqual(server.address, "127.0.0.1")
            self.assertEqual(server.port, "50000")
            mock_add_servicer.assert_called_once()
            mock_server.assert_called_once()
            mock_server_instance.add_insecure_port.assert_called_once_with("127.0.0.1:50000")
            mock_server_instance.start.assert_called_once()
            mock_server_instance.wait_for_termination.assert_called_once()

            token = b'token'
            self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
            seed = b'\xa8\xce\x88\xf0}\xed4\x850\xa6&s\xc2\xd1\x81\x8f\xbe\xfd\xae>BO\xb1$\xec\xe2O\xca\xc6k\x08D'
            request = voting_pb2.AuthRequest(name = voting_pb2.VoterName(name = 'jiregjwgqffqqf'), response = voting_pb2.Response(value = SigningKey(seed).sign(b'Challenge').signature))
            response = self.evs.Auth(request, None)
            self.assertIsInstance(response.value, bytes)
        print("test_Auth_3")
    
    def test_CreateElection_valid_1(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Election()
        request.token.value = b'token'
        request.name = 'election1'
        request.choices.append('students')
        request.groups.append('A')
        request.groups.append('B')
        request.end_date.GetCurrentTime()
        request.end_date.seconds = int(datetime.now().timestamp() + 3600)
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,0)
        print("test_CreateElection_valid_1")
    
    def test_CreateElection_valid_2(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Election()
        request.token.value = b'154556'
        request.name = 'wegwe'
        request.choices.append('affwfaf')
        request.groups.append('vsc')
        request.groups.append('awad')
        request.end_date.GetCurrentTime()
        request.end_date.seconds = int(datetime.now().timestamp() + 3600)
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,0)
        print("test_CreateElection_valid_2")
    
    def test_CreateElection_valid_3(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Election()
        request.token.value = b'wwwgwwe'
        request.name = 'esebbs'
        request.choices.append('wgagaw')
        request.groups.append('aga')
        request.groups.append('rgrr')
        request.end_date.GetCurrentTime()
        request.end_date.seconds = int(datetime.now().timestamp() + 3600)
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,0)
        print("test_CreateElection_valid_3")

    def test_CreateElection_valid_4(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Election()
        request.token.value = b'gwgwwwa'
        request.name = 'ggsdgd'
        request.choices.append('seqqg')
        request.groups.append('aeaef')
        request.groups.append('vdv')
        request.end_date.GetCurrentTime()
        request.end_date.seconds = int(datetime.now().timestamp() + 3600)
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,0)
        print("test_CreateElection_valid_4")
    
    def test_CreateElection_valid_5(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Election()
        request.token.value = b'qfqfq'
        request.name = 'dvas'
        request.choices.append('qqwfas')
        request.groups.append('aavs')
        request.groups.append('vasva')
        request.end_date.GetCurrentTime()
        request.end_date.seconds = int(datetime.now().timestamp() + 3600)
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,0)
        print("test_CreateElection_valid_5")
    
    def test_CreateElection_valid_6(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Election()
        request.token.value = b'gewggwg'
        request.name = 'rwewge'
        request.choices.append('w4qwg')
        request.groups.append('gwgw')
        request.groups.append('dgvsgg')
        request.end_date.GetCurrentTime()
        request.end_date.seconds = int(datetime.now().timestamp() + 3600)
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,0)
        print("test_CreateElection_valid_6")
    
    def test_CreateElection_valid_7(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Election()
        request.token.value = b'663g4gw'
        request.name = 'vszv'
        request.choices.append('zbdzr')
        request.groups.append('sbbs')
        request.groups.append('Wqqgg')
        request.end_date.GetCurrentTime()
        request.end_date.seconds = int(datetime.now().timestamp() + 3600)
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,0)
        print("test_CreateElection_valid_7")

    def test_CreateElection_invalid_1(self):  # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        response = self.evs.CreateElection(voting_pb2.Election(), None)
        self.assertEqual(response.code,1)
        print("test_CreateElection_invalid_1")

    def test_CreateElection_invalid_2(self):  # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        response = self.evs.CreateElection(voting_pb2.Election(), None)
        self.assertEqual(response.code,2)
        print("test_CreateElection_invalid_2")
    
    def test_CreateElection_invalid_3(self):  # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Election()
        request.token.value = b'663g4gw'
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,1)
        print("test_CreateElection_invalid_3")
    
    def test_CreateElection_invalid_4(self):  # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Election()
        request.token.value = b'663g4gw'
        request.groups.append('sbbs')
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,1)
        print("test_CreateElection_invalid_4")
    
    def test_CreateElection_invalid_5(self):  # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Election()
        request.token.value = b'663g4gw'
        request.groups.append('21565')
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,1)
        print("test_CreateElection_invalid_5")
    
    def test_CreateElection_invalid_6(self):  # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Election()
        request.token.value = b'15616'
        request.groups.append('8569')
        request.end_date.seconds = int(datetime.now().timestamp() + 3600)
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,1)
        print("test_CreateElection_invalid_6")
    
    def test_CreateElection_invalid_7(self):  # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Election()
        request.token.value = b'gage'
        request.groups.append('156')
        request.end_date.seconds = int(datetime.now().timestamp() + 3600)
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,1)
        print("test_CreateElection_invalid_7")

    def test_CreateElection_invalid_8(self):  # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Election()
        request.token.value = b'weggg'
        request.groups.append('aqgeges')
        request.end_date.seconds = int(datetime.now().timestamp() + 3600)
        response = self.evs.CreateElection(request, None)
        self.assertEqual(response.code,1)
        print("test_CreateElection_invalid_8")
    
    def test_CreateElection_invalid_9(self):  # 共6種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        test_data = [b'weggg',b'wavjajv',b'dkkjava',b'aovjaii',b'jeijqijoa',b'ijefilaf']
        for test in test_data:
            request = voting_pb2.Election()
            request.token.value = test
            response = self.evs.CreateElection(request, None)
            self.assertEqual(response.code,2)
        print("test_CreateElection_invalid_9")

    def test_CastVote_valid_1(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'token'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        self.evs.election = {"Hi":{"group":["students"],"voted":[],"endate":123456789,"A":0,"B":0}}
        request = voting_pb2.Vote(
            election_name = "Hi", 
            choice_name = "A",
            token = voting_pb2.AuthToken(value= b'token')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,0)
        print("test_CastVote_valid_1")

    def test_CastVote_valid_2(self):  # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'16464'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Alice', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        self.evs.election = {"mslamcsa":{"group":["students"],"voted":[],"endate":123456789,"jaosc":0,"sjea":0}}
        request = voting_pb2.Vote(
            election_name = "mslamcsa", 
            choice_name = "sjea",
            token = voting_pb2.AuthToken(value= b'16464')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,0)
        print("test_CastVote_valid_2")
    
    def test_CastVote_valid_3(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'3jwliqjlf'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['wejo;wfjw;e', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        self.evs.election = {"afasfasv":{"group":["students"],"voted":[],"endate":123456789,"avav":0,"B":0}}
        request = voting_pb2.Vote(
            election_name = "afasfasv", 
            choice_name = "avav",
            token = voting_pb2.AuthToken(value= b'3jwliqjlf')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,0)
        print("test_CastVote_valid_3")
    
    def test_CastVote_valid_4(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'ehahreg'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['aegvdzv', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        self.evs.election = {"zvzvzv":{"group":["students"],"voted":[],"endate":5156164561165,"vavdvd":0,"advav":0}}
        request = voting_pb2.Vote(
            election_name = "zvzvzv", 
            choice_name = "vavdvd",
            token = voting_pb2.AuthToken(value= b'ehahreg')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,0)
        print("test_CastVote_valid_4")

    def test_CastVote_valid_5(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'aafafafas'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        self.evs.election = {"vvsvaxx":{"group":["students"],"voted":[],"endate":123456789,"zzvsvs":0,"afasf":0}}
        request = voting_pb2.Vote(
            election_name = "vvsvaxx", 
            choice_name = "zzvsvs",
            token = voting_pb2.AuthToken(value= b'aafafafas')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,0)
        print("test_CastVote_valid_5")
    
    def test_CastVote_valid_6(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'regdgdsa'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        self.evs.election = {"adsfafa":{"group":["students"],"voted":[],"endate":123456789,"davasvas":0,"avsvssa":0}}
        request = voting_pb2.Vote(
            election_name = "adsfafa", 
            choice_name = "davasvas",
            token = voting_pb2.AuthToken(value= b'regdgdsa')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,0)
        print("test_CastVote_valid_6")
    
    def test_CastVote_valid_7(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'gfdsgafgs'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        self.evs.election = {"efeqqfqefea":{"group":["students"],"voted":[],"endate":123456789,"advavs":0,"kgjfghdfgdf":0}}
        request = voting_pb2.Vote(
            election_name = "efeqqfqefea", 
            choice_name = "advavs",
            token = voting_pb2.AuthToken(value= b'gfdsgafgs')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,0)
        print("test_CastVote_valid_7")

# 54種情況

    def test_CastVote_invalid_1_1(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        response = self.evs.CastVote(voting_pb2.Vote(), None)
        self.assertEqual(response.code,1)
        print("test_CastVote_invalid_1_1")
    
    def test_CastVote_invalid_1_2(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Vote(
            election_name = "grsg", 
            choice_name = "wegwe",
            token = voting_pb2.AuthToken(value= b'gwga')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,1)
        print("test_CastVote_invalid_1_2")

    def test_CastVote_invalid_1_3(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Vote(
            election_name = "eqfaefe", 
            choice_name = "avavadv",
            token = voting_pb2.AuthToken(value= b'qefqeg')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,1)
        print("test_CastVote_invalid_1_3")

    def test_CastVote_invalid_1_4(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Vote(
            election_name = "dgaga", 
            choice_name = "aesdssvs",
            token = voting_pb2.AuthToken(value= b'gwwsd')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,1)
        print("test_CastVote_invalid_1_4")
    
    def test_CastVote_invalid_1_5(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Vote(
            election_name = "egwefew", 
            choice_name = "svsavads",
            token = voting_pb2.AuthToken(value= b'wegwegs')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,1)
        print("test_CastVote_invalid_1_5")
    
    def test_CastVote_invalid_1_6(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Vote(
            election_name = "asvavd", 
            choice_name = "aavdc",
            token = voting_pb2.AuthToken(value= b'sdvdvzvz')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,1)
        print("test_CastVote_invalid_1_6")
    
    def test_CastVote_invalid_1_7(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = False)
        request = voting_pb2.Vote(
            election_name = "dfghjg", 
            choice_name = "dxfcgrhte",
            token = voting_pb2.AuthToken(value= b'fzdgcvgdste')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,1)
        print("test_CastVote_invalid_1_7")
    
    def test_CastVote_invalid_2_1(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        response = self.evs.CastVote(voting_pb2.Vote(), None)
        self.assertEqual(response.code,2)
        print("test_CastVote_invalid_2_1")
    
    def test_CastVote_invalid_2_2(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Vote(
            election_name = "uytr", 
            choice_name = "srdthgdfs",
            token = voting_pb2.AuthToken(value= b'adsdrd')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,2)
        print("test_CastVote_invalid_2_2")

    def test_CastVote_invalid_2_3(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Vote(
            election_name = "tyjrth", 
            choice_name = "erhwhwr",
            token = voting_pb2.AuthToken(value= b'wehtj')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,2)
        print("test_CastVote_invalid_2_3")
    
    def test_CastVote_invalid_2_4(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Vote(
            election_name = "erdhtj", 
            choice_name = "asrhdtfjy",
            token = voting_pb2.AuthToken(value= b'wegsd')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,2)
        print("test_CastVote_invalid_2_4")

    def test_CastVote_invalid_2_5(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Vote(
            election_name = "yuktjfgbdf", 
            choice_name = "weryt",
            token = voting_pb2.AuthToken(value= b'6urthgf')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,2)
        print("test_CastVote_invalid_2_5")
    
    def test_CastVote_invalid_2_6(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Vote(
            election_name = "tyhrtg", 
            choice_name = "dyrthrg",
            token = voting_pb2.AuthToken(value= b'esrydt')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,2)
        print("test_CastVote_invalid_2_6")
    
    def test_CastVote_invalid_2_7(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        request = voting_pb2.Vote(
            election_name = "jkutyjd", 
            choice_name = "tryfgndfbdssegr",
            token = voting_pb2.AuthToken(value= b'bsdaetw4yerhd')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,2)
        print("test_CastVote_invalid_2_7")
    
    def test_CastVote_invalid_3_1(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'token'
        self.evs.election = {"Hi":{"group":["students"],"voted":[],"endate":123456789,"A":0,"B":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'A']
        request = voting_pb2.Vote(
            election_name = "Hi", 
            choice_name = "A",
            token = voting_pb2.AuthToken(value= b'token')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,3)
        print("test_CastVote_invalid_3_1")
    
    def test_CastVote_invalid_3_2(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'token'
        self.evs.election = {"liykujyht":{"group":["zdxgftfy"],"voted":[],"endate":123456789,"ersgefs":0,"B":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'A']
        request = voting_pb2.Vote(
            election_name = "liykujyht", 
            choice_name = "ersgefs",
            token = voting_pb2.AuthToken(value= b'token')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,3)
        print("test_CastVote_invalid_3_2")
    
    def test_CastVote_invalid_3_3(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'sftyjfhdf'
        self.evs.election = {"fhdfsvd":{"group":["qwedfgh"],"voted":[],"endate":123456789,"ersgefs":0,"B":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'A']
        request = voting_pb2.Vote(
            election_name = "fhdfsvd", 
            choice_name = "ersgefs",
            token = voting_pb2.AuthToken(value= b'sftyjfhdf')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,3)
        print("test_CastVote_invalid_3_3")
    
    def test_CastVote_invalid_3_4(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'utrhrgrsd'
        self.evs.election = {"bfty":{"group":["esrht"],"voted":[],"endate":123456789,"dfdg":0,"erty":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'A']
        request = voting_pb2.Vote(
            election_name = "bfty", 
            choice_name = "dfdg",
            token = voting_pb2.AuthToken(value= b'utrhrgrsd')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,3)
        print("test_CastVote_invalid_3_4")
    
    def test_CastVote_invalid_3_5(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'utrhrgrsd'
        self.evs.election = {"aesrdt":{"group":["wefg"],"voted":[],"endate":123456789,"dsfdgfghg":0,"erty":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'A']
        request = voting_pb2.Vote(
            election_name = "aesrdt", 
            choice_name = "dsfdgfghg",
            token = voting_pb2.AuthToken(value= b'utrhrgrsd')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,3)
        print("test_CastVote_invalid_3_5")
    
    def test_CastVote_invalid_3_6(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'gdgf'
        self.evs.election = {"svcxczx":{"group":["ughgff"],"voted":[],"endate":123456789,"dsfdgfghg":0,"erty":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'A']
        request = voting_pb2.Vote(
            election_name = "svcxczx", 
            choice_name = "dsfdgfghg",
            token = voting_pb2.AuthToken(value= b'gdgf')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,3)
        print("test_CastVote_invalid_3_6")
    
    def test_CastVote_invalid_3_7(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'wewe56'
        self.evs.election = {"etrytyg":{"group":["ughgff"],"voted":[],"endate":123456789,"dsfdgfghg":0,"erty":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'A']
        request = voting_pb2.Vote(
            election_name = "etrytyg", 
            choice_name = "dsfdgfghg",
            token = voting_pb2.AuthToken(value= b'wewe56')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,3)
        print("test_CastVote_invalid_3_7")
# 75種情況
    def test_CastVote_invalid_4_1(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'token'
        self.evs.election = {"Hi":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":123456789,"A":0,"B":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        request = voting_pb2.Vote(
            election_name = "Hi", 
            choice_name = "A",
            token = voting_pb2.AuthToken(value= b'token')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,4)
        print("test_CastVote_invalid_4_1")

    def test_CastVote_invalid_4_2(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'yjthrg'
        self.evs.election = {"tyrhd":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":123456789,"rgsd":0,"B":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        request = voting_pb2.Vote(
            election_name = "tyrhd", 
            choice_name = "rgsd",
            token = voting_pb2.AuthToken(value= b'yjthrg')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,4)
        print("test_CastVote_invalid_4_2") 
    
    def test_CastVote_invalid_4_3(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'adxccs'
        self.evs.election = {"iujhg":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":123456789,"erdgh":0,"rgfh":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        request = voting_pb2.Vote(
            election_name = "iujhg", 
            choice_name = "erdgh",
            token = voting_pb2.AuthToken(value= b'adxccs')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,4)
        print("test_CastVote_invalid_4_3") 
    
    def test_CastVote_invalid_4_4(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'mmhng'
        self.evs.election = {"oingbfv":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":123456789,"srdtfy":0,"rgfh":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        request = voting_pb2.Vote(
            election_name = "oingbfv", 
            choice_name = "srdtfy",
            token = voting_pb2.AuthToken(value= b'mmhng')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,4)
        print("test_CastVote_invalid_4_4") 
    
    def test_CastVote_invalid_4_5(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'wert'
        self.evs.election = {"iyughg":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":123456789,"srhdth":0,"rgfh":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        request = voting_pb2.Vote(
            election_name = "iyughg", 
            choice_name = "srhdth",
            token = voting_pb2.AuthToken(value= b'wert')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,4)
        print("test_CastVote_invalid_4_5") 
    
    def test_CastVote_invalid_4_6(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'afgsdhgkj'
        self.evs.election = {"asdg":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":123456789,"dgsfdhgfh":0,"rgfh":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        request = voting_pb2.Vote(
            election_name = "asdg", 
            choice_name = "dgsfdhgfh",
            token = voting_pb2.AuthToken(value= b'afgsdhgkj')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,4)
        print("test_CastVote_invalid_4_6")
    
    def test_CastVote_invalid_4_7(self): # 共1種情況
        self.evs.VerifyAuthToken = Mock(return_value = True)
        token = b'7uysdf'
        self.evs.election = {"ddjhjgf":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":123456789,"rdawsasz":0,"rgfh":0}}
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['Bob', (datetime.now() + timedelta(hours=1)).timestamp(), 'students']
        request = voting_pb2.Vote(
            election_name = "ddjhjgf", 
            choice_name = "rdawsasz",
            token = voting_pb2.AuthToken(value= b'7uysdf')
        )
        response = self.evs.CastVote(request, None)
        self.assertEqual(response.code,4)
        print("test_CastVote_invalid_4_7")

    def test_GetResult_valid_1(self): # 共1種情況
        token = b'token'
        dt = datetime.fromisoformat("2023-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"Hi":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "Hi")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,0)
        print("test_GetResult_valid_1")

    def test_GetResult_valid_2(self): # 共1種情況
        token = b'utyjthdgsd'
        dt = datetime.fromisoformat("2023-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"xzdxfd":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "xzdxfd")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,0)
        print("test_GetResult_valid_2")
    
    def test_GetResult_valid_3(self): # 共1種情況
        token = b'ytrgdfzas'
        dt = datetime.fromisoformat("2023-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"qwasd":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "qwasd")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,0)
        print("test_GetResult_valid_3")

    def test_GetResult_valid_4(self): # 共1種情況
        token = b'xdgcfhvgjhbk'
        dt = datetime.fromisoformat("2023-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"dxgcfhgvjbh":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "dxgcfhgvjbh")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,0)
        print("test_GetResult_valid_4")
    
    def test_GetResult_valid_5(self): # 共1種情況
        token = b'dgcfhvgjbhk'
        dt = datetime.fromisoformat("2023-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"rfygvjbhkn":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "rfygvjbhkn")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,0)
        print("test_GetResult_valid_5")
    
    def test_GetResult_valid_6(self): # 共1種情況
        token = b'xcgfghvhjj'
        dt = datetime.fromisoformat("2023-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"cdfhvgjbhknj":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "cdfhvgjbhknj")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,0)
        print("test_GetResult_valid_6")
    
    def test_GetResult_valid_7(self): # 共1種情況
        token = b'cdgfvhgbjhnk'
        dt = datetime.fromisoformat("2023-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"szfxdgcfhvgbh":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "szfxdgcfhvgbh")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,0)
        print("test_GetResult_valid_7")
    
    def test_GetResult_invalid_1_1(self): # 共1種情況
        request = voting_pb2.ElectionName(name = "Hi")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,1)
        print("test_GetResult_invalid_1_1")
    
    def test_GetResult_invalid_1_2(self): # 共1種情況
        request = voting_pb2.ElectionName(name = "dcfvhgbhjknjml")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,1)
        print("test_GetResult_invalid_1_2")
    
    def test_GetResult_invalid_1_3(self): # 共1種情況
        request = voting_pb2.ElectionName(name = "zssdxfgcghvg")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,1)
        print("test_GetResult_invalid_1_3")
    
    def test_GetResult_invalid_1_4(self): # 共1種情況
        request = voting_pb2.ElectionName(name = "dsdfhgjhbjk")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,1)
        print("test_GetResult_invalid_1_4")
    
    def test_GetResult_invalid_1_5(self): # 共1種情況
        request = voting_pb2.ElectionName(name = "iyutytd")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,1)
        print("test_GetResult_invalid_1_5")
    
    def test_GetResult_invalid_1_6(self): # 共1種情況
        request = voting_pb2.ElectionName(name = "dvasftjythf")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,1)
        print("test_GetResult_invalid_1_6")
    
    def test_GetResult_invalid_1_7(self): # 共1種情況
        request = voting_pb2.ElectionName(name = "ZSZerdytf")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,1)
        print("test_GetResult_invalid_1_7")
    
    def test_GetResult_invalid_2_1(self): # 共1種情況
        token = b'token'
        dt = datetime.fromisoformat("3000-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"Hi":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "Hi")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,2)
        print("test_GetResult_invalid_2_1")
    
    def test_GetResult_invalid_2_2(self): # 共1種情況
        token = b'sadsfdhtfy'
        dt = datetime.fromisoformat("3000-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"dsfdgh":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "dsfdgh")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,2)
        print("test_GetResult_invalid_2_2")

    def test_GetResult_invalid_2_3(self): # 共1種情況
        token = b'xdgcfhgvjbjk'
        dt = datetime.fromisoformat("3000-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"dztd":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "dztd")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,2)
        print("test_GetResult_invalid_2_3")
    
    def test_GetResult_invalid_2_4(self): # 共1種情況
        token = b'xdfcvghb'
        dt = datetime.fromisoformat("3000-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"waesrd":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "waesrd")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,2)
        print("test_GetResult_invalid_2_4")
    
    def test_GetResult_invalid_2_5(self): # 共1種情況
        token = b'sdgfdhgfhg'
        dt = datetime.fromisoformat("3000-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"dsfg":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "dsfg")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,2)
        print("test_GetResult_invalid_2_5")
    
    def test_GetResult_invalid_2_6(self): # 共1種情況
        token = b'WAESDR'
        dt = datetime.fromisoformat("3000-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"DFDGFH":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "DFDGFH")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,2)
        print("test_GetResult_invalid_2_6")
    
    def test_GetResult_invalid_2_7(self): # 共1種情況
        token = b'dwert'
        dt = datetime.fromisoformat("3000-01-01T00:00:00")
        end_date = Timestamp()
        end_date.FromDatetime(dt)
        self.evs.election = {"sdsdfg":{"group":["students"],"voted":[Base64Encoder.encode(token)],"endate":end_date,"A":0,"B":0}}
        request = voting_pb2.ElectionName(name = "sdsdfg")
        response = self.evs.GetResult(request, None)
        self.assertEqual(response.status,2)
        print("test_GetResult_invalid_2_7")

    @patch('voting_server.grpc.server')
    @patch('voting_server.voting_pb2_grpc.add_eVotingServicer_to_server')
    @patch('builtins.input', side_effect=["1", "127.0.0.1", "50000"])
    def test_init_and_Reg(self, mock_input, mock_add_servicer, mock_server): # 共8個測試
        mock_server_instance = mock_server.return_value
        mock_server_instance.wait_for_termination = Mock()
        voter_data = "Bob students qM6I8H3tNIUwpiZzwtGBj779rj5CT7Ek7OJPysZrCEQ=\n"
        with patch('builtins.open', return_value=io.StringIO(voter_data)) as mock_file,patch('builtins.print') as mock_print:
            server = voting_server.serve()
            self.assertEqual(server.api_call, "1")
            self.assertEqual(server.address, "127.0.0.1")
            self.assertEqual(server.port, "50000")
            mock_add_servicer.assert_called_once()
            mock_server.assert_called_once()
            mock_server_instance.add_insecure_port.assert_called_once_with("127.0.0.1:50000")
            mock_server_instance.start.assert_called_once()
            mock_server_instance.wait_for_termination.assert_called_once()

            server.api_call = "1"
            voter_data = "Bob students qM6I8H3tNIUwpiZzwtGBj779rj5CT7Ek7OJPysZrCEQ=\n"
            with patch('builtins.open', return_value=io.StringIO(voter_data)) as mock_file:
                server.Reg()

            server.api_call = "3"
            self.assertEqual(server.Reg(),{'Bob': ('students', b'\xd8-V\xee\xb7\x9c\xfa\x1b\x1b\xc4\xac\x19U\r\xa0\xda\xec\xfc\xdf\xb3\xc6\xdd\n\x86\xcc\xbau8\xa5k\xaa\xc7')})
            
            server.api_call = "2"
            with patch('builtins.input', return_value="Bob"):
                self.assertEqual(server.Reg(),{})

            server.api_call = "2"
            with patch('builtins.input', return_value="Alice"):
                server.Reg()
                mock_print.assert_called_with('Status : ', 1)
            
            server.api_call = "4"
            server.Reg()
            mock_print.assert_called_with('Invalid input.\n')

            server.api_call = "2"
            with patch('builtins.input', return_value="Bob"):
                server.Reg()
                mock_print.assert_called_with('Status : ', 1)
            
            server.api_call = "3"
            self.assertEqual(server.Reg(),{})
            
            server.api_call = "4"
            server.Reg()
            mock_print.assert_called_with('Invalid input.\n')

if __name__ == '__main__': # pragma: no cover
    unittest.main()

# 總共111筆測資