import sys
import unittest
import io
from unittest.mock import Mock,patch,MagicMock
sys.path.append(r"..\Test-Target")
import voting_server
import voting_pb2
from nacl.encoding import Base64Encoder
import voting_pb2_grpc
from datetime import datetime, timedelta
from parameterized import parameterized
from nacl.signing import SigningKey

class Test(unittest.TestCase):
    # def test_RegisterVoter_Exception(self):
    #     voter = voting_pb2.Voter(name=b"test", group=b"group", public_key=b"public_key")
    #     # with self.assertRaises(Exception) as cm:
    #     #     service = voting_server.LocalService()
    #     #     service.RegisterVoter = Mock(side_effect=Exception("Something went wrong"))
    #     #     result = service.RegisterVoter(voter)
    #     #     self.assertEqual(result.code, 2)
    #     with patch.dict('voting_server.Voter_dict', side_effect=Exception('something went wrong')):
    #         with self.assertRaises(Exception):
    #             service = LocalService()
    #             result = service.RegisterVoter(voter)
    def setUp(self):
        self.evs = voting_server.eVotingServicer()

    def test_VerifyAuthToken(self):
        token = b'token'
        self.assertEqual(self.evs.VerifyAuthToken(token), False)
        token = b'token'
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['John', (datetime.now() + timedelta(hours=1)).timestamp(), 'A']
        self.assertEqual(self.evs.VerifyAuthToken(token), True)
        self.evs.auth_tokens[Base64Encoder.encode(token)] = ['John', (datetime.now() - timedelta(hours=1)).timestamp(), 'A']
        self.assertEqual(self.evs.VerifyAuthToken(token), False)
    
    def test_PreAuth(self):
        challenge = self.evs.PreAuth(None, None)
        self.assertEqual(challenge.value, b'Challenge')

    @patch('voting_server.grpc.server')
    @patch('voting_server.voting_pb2_grpc.add_eVotingServicer_to_server')
    @patch('builtins.input', side_effect=["1", "127.0.0.1", "50000"])
    def test_Auth(self, mock_input, mock_add_servicer, mock_server):
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
    
    @patch('voting_server.grpc.server')
    @patch('voting_server.voting_pb2_grpc.add_eVotingServicer_to_server')
    @patch('builtins.input', side_effect=["1", "127.0.0.1", "50000"])
    def test_init_and_Reg(self, mock_input, mock_add_servicer, mock_server):
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

if __name__ == '__main__': # pragma: no cover
    unittest.main()
