import sys
import unittest
import io
from unittest.mock import Mock,patch,MagicMock
sys.path.append(r"..\Test-Target")
import voting_server
from parameterized import parameterized

class Test(unittest.TestCase):
    @patch('voting_server.grpc.server')
    @patch('voting_server.voting_pb2_grpc.add_eVotingServicer_to_server')
    @patch('builtins.input', side_effect=["1", "127.0.0.1", "50000"])
    def test_init_and_Reg(self, mock_input, mock_add_servicer, mock_server):
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
            server.api_call = "2"
            with patch('builtins.input', return_value="Bob"):
                server.Reg()
            server.api_call = "3"
            server.Reg()
            server.api_call = "4"
            server.Reg()

if __name__ == '__main__': # pragma: no cover
    unittest.main()
