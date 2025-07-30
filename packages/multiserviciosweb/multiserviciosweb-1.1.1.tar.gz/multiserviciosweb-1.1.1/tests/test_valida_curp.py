"""
Unit tests for ValidaCurp Python client.
"""

import unittest
from unittest.mock import Mock, patch
import json

from MultiServiciosWeb import ValidaCurp, ValidaCurpException


class TestValidaCurpClient(unittest.TestCase):
    """Test cases for ValidaCurp Client."""

    def setUp(self):
        """Set up test fixtures."""
        self.token = "test-token"
        self.client = ValidaCurp(self.token)
        self.test_curp = "PXNE660720HMCXTN06"

    def test_init(self):
        """Test client initialization."""
        self.assertEqual(self.client.get_token(), self.token)
        self.assertEqual(self.client.get_version(), 2)
        self.assertEqual(self.client.get_endpoint(), ValidaCurp.URL_V2)

    def test_init_with_custom_endpoint(self):
        """Test client initialization with custom endpoint."""
        custom_endpoint = "https://custom.example.com/api/"
        client = ValidaCurp(self.token, custom_endpoint)
        self.assertEqual(client.get_endpoint(), custom_endpoint)

    def test_set_version_v1(self):
        """Test setting API version to 1."""
        self.client.set_version(1)
        self.assertEqual(self.client.get_version(), 1)
        self.assertEqual(self.client.get_endpoint(), ValidaCurp.URL_V1)

    def test_set_version_v2(self):
        """Test setting API version to 2."""
        self.client.set_version(2)
        self.assertEqual(self.client.get_version(), 2)
        self.assertEqual(self.client.get_endpoint(), ValidaCurp.URL_V2)

    def test_set_version_invalid(self):
        """Test setting invalid API version."""
        with self.assertRaises(ValidaCurpException):
            self.client.set_version(3)

    @patch('valida_curp.client.requests.get')
    def test_is_valid_v1_success(self, mock_get):
        """Test is_valid method with API v1 success."""
        self.client.set_version(1)

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {"valido": 1}
        }
        mock_get.return_value = mock_response

        result = self.client.is_valid(self.test_curp)
        self.assertEqual(result, {"valido": 1})

        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args[0][0]
        self.assertIn("validar", call_args)
        self.assertIn(self.test_curp, call_args)
        self.assertIn(self.token, call_args)

    @patch('valida_curp.client.requests.post')
    def test_is_valid_v2_success(self, mock_post):
        """Test is_valid method with API v2 success."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {"valido": 1}
        }
        mock_post.return_value = mock_response

        result = self.client.is_valid(self.test_curp)
        self.assertEqual(result, {"valido": 1})

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args, call_kwargs = mock_post.call_args
        self.assertIn("validateCurpStructure", call_args[0])
        self.assertEqual(call_kwargs["json"]["curp"], self.test_curp)
        self.assertEqual(call_kwargs["json"]["token"], self.token)

    def test_is_valid_no_token(self):
        """Test is_valid method without token."""
        client = ValidaCurp("")
        with self.assertRaises(ValidaCurpException) as context:
            client.is_valid(self.test_curp)
        self.assertIn("token was not set", str(context.exception))

    @patch('valida_curp.client.requests.post')
    def test_is_valid_auth_error(self, mock_post):
        """Test is_valid method with authentication error."""
        # Mock authentication error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "msn": "Invalid token"
        }
        mock_post.return_value = mock_response

        with self.assertRaises(ValidaCurpException) as context:
            self.client.is_valid(self.test_curp)
        self.assertIn("Failed authentication", str(context.exception))

    @patch('valida_curp.client.requests.post')
    def test_get_data_success(self, mock_post):
        """Test get_data method success."""
        # Mock successful response
        mock_response_data = {
            "response": {
                "Applicant": {
                    "CURP": self.test_curp,
                    "Names": "ENRIQUE",
                    "LastName": "PEÑA"
                }
            }
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response

        result = self.client.get_data(self.test_curp)
        self.assertEqual(result, mock_response_data["response"])

    def test_calculate_missing_data(self):
        """Test calculate method with missing required data."""
        incomplete_data = {
            "names": "Enrique",
            "lastName": "Peña"
            # Missing other required fields
        }

        with self.assertRaises(ValidaCurpException) as context:
            self.client.calculate(incomplete_data)
        self.assertIn("was not set", str(context.exception))

    @patch('valida_curp.client.requests.post')
    def test_calculate_v2_success(self, mock_post):
        """Test calculate method with API v2 success."""
        person_data = {
            'names': 'Enrique',
            'lastName': 'Peña',
            'secondLastName': 'Nieto',
            'birthDay': '20',
            'birthMonth': '07',
            'birthYear': '1966',
            'gender': 'H',
            'entity': '15',
        }

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {"curp": self.test_curp}
        }
        mock_post.return_value = mock_response

        result = self.client.calculate(person_data)
        self.assertEqual(result, {"curp": self.test_curp})

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args, call_kwargs = mock_post.call_args
        self.assertIn("calculateCURP", call_args[0])

        # Check that birthDay was renamed to birthday and birthYear to yearBirth
        json_data = call_kwargs["json"]
        self.assertEqual(json_data["birthday"], "20")
        self.assertEqual(json_data["yearBirth"], "1966")
        self.assertNotIn("birthDay", json_data)
        self.assertNotIn("birthYear", json_data)

    @patch('valida_curp.client.requests.get')
    def test_calculate_v1_success(self, mock_get):
        """Test calculate method with API v1 success."""
        self.client.set_version(1)

        person_data = {
            'names': 'Enrique',
            'lastName': 'Peña',
            'secondLastName': 'Nieto',
            'birthDay': '20',
            'birthMonth': '07',
            'birthYear': '1966',
            'gender': 'H',
            'entity': '15',
        }

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {"curp": self.test_curp}
        }
        mock_get.return_value = mock_response

        result = self.client.calculate(person_data)
        self.assertEqual(result, {"curp": self.test_curp})

        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args[0][0]
        self.assertIn("calcular_curp", call_args)
        # Check that the data was transformed for v1 API
        self.assertIn("nombres=Enrique", call_args)
        self.assertIn("apellido_paterno=Pe%C3%B1a", call_args)

    @patch('valida_curp.client.requests.post')
    def test_get_entities_success(self, mock_post):
        """Test get_entities method success."""
        # Mock successful response
        mock_entities = {
            "response": {
                "clave_entidad": [
                    {
                        "clave_entidad": "01",
                        "nombre_entidad": "AGUASCALIENTES",
                        "abreviatura_entidad": "AS"
                    }
                ]
            }
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_entities
        mock_post.return_value = mock_response

        result = self.client.get_entities()
        self.assertEqual(result, mock_entities["response"])

    def test_make_url_v1(self):
        """Test URL building for API v1."""
        self.client.set_version(1)
        url = self.client._make_url("test_method", self.test_curp)

        self.assertIn(ValidaCurp.URL_V1, url)
        self.assertIn("test_method", url)
        self.assertIn(f"curp={self.test_curp}", url)
        self.assertIn(f"token={self.token}", url)
        self.assertIn("library=python_pip", url)
        self.assertIn("api_version=1", url)


if __name__ == '__main__':
    unittest.main()