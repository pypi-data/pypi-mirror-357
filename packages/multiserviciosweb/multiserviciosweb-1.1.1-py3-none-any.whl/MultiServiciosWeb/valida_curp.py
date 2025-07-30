"""
ValidaCurp Client

This library can validate, calculate and obtain CURP information in México.

Copyright (c) Multiservicios Web JCA S.A. de C.V., https://multiservicios-web.com.mx
License: MIT (https://opensource.org/license/MIT)

Author: Joel Rojas <me@hckdrk.mx>
"""

import json
import os
from typing import Dict, Any, Optional
from urllib.parse import urlencode

import requests
from requests.exceptions import RequestException


class ValidaCurp:
    """ValidaCurp API Client for Python."""

    URL_V1 = "https://api.valida-curp.com.mx/curp/"
    URL_V2 = "https://version.valida-curp.com.mx/api/v2/curp/"

    LIBRARY_VERSION = "1.1.0"
    TYPE = "python"

    def __init__(self, token: Optional[str] = None, custom_endpoint: Optional[str] = None):
        """
        Initialize the ValidaCurp client.

        Args:
            token (str): The project token
            custom_endpoint (str, optional): Custom endpoint URL
        """
        if token:
            self.token = token
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.token = os.environ.get('TOKEN_VALIDA_API_CURP')
        self.version = 2
        self.endpoint = custom_endpoint or self.URL_V2
        self.custom_endpoint = custom_endpoint

    def get_version(self) -> int:
        """Get the current API version."""
        return self.version

    def set_version(self, version: int = 2) -> None:
        """
        Set the API version.

        Version 1 of the API is deprecated. Please use version 2 of the API.

        Args:
            version (int): API version (1 or 2)

        Raises:
            ValidaCurpException: If version is invalid
        """
        if version == 1:
            self.version = 1
            self.endpoint = self.custom_endpoint or self.URL_V1
        elif version == 2:
            self.version = 2
            self.endpoint = self.custom_endpoint or self.URL_V2
        else:
            raise ValidaCurpException("The version is invalid")

    def get_endpoint(self) -> str:
        """Get the current endpoint URL."""
        return self.endpoint

    def get_token(self) -> str:
        """Get the current token."""
        return self.token

    def is_valid(self, curp: str) -> Dict[str, Any]:
        """
        Validate CURP structure.

        This method takes a CURP as a parameter and validates the structure.

        Args:
            curp (str): The CURP to validate

        Returns:
            dict: Validation response

        Raises:
            ValidaCurpException: If token is not set or API error occurs
            RequestException: If HTTP request fails
        """
        if not self.get_token():
            raise ValidaCurpException("The token was not set")

        if self.get_version() == 1:
            return self._validate_v1(curp)
        else:
            return self._validate_v2(curp)

    def _validate_v1(self, curp: str) -> Dict[str, Any]:
        """Validate CURP using API v1."""
        url = self._make_url("validar", curp)
        response = self._request_get(url)
        return self._decode_response(response)

    def _validate_v2(self, curp: str) -> Dict[str, Any]:
        """Validate CURP using API v2."""
        response = self._make_request("validateCurpStructure", curp)
        return self._decode_response(response)

    def get_data(self, curp: str) -> Dict[str, Any]:
        """
        Get CURP data from RENAPO.

        This method takes a CURP as a parameter and consults the CURP information in RENAPO.

        Args:
            curp (str): The CURP to query

        Returns:
            dict: CURP data response

        Raises:
            ValidaCurpException: If token is not set or API error occurs
            RequestException: If HTTP request fails
        """
        if not self.get_token():
            raise ValidaCurpException("The token was not set")

        if self.get_version() == 1:
            return self._get_data_v1(curp)
        else:
            return self._get_data_v2(curp)

    def _get_data_v1(self, curp: str) -> Dict[str, Any]:
        """Get CURP data using API v1."""
        url = self._make_url("obtener_datos", curp)
        response = self._request_get(url)
        return self._decode_response(response)

    def _get_data_v2(self, curp: str) -> Dict[str, Any]:
        """Get CURP data using API v2."""
        response = self._make_request("getData", curp)
        return self._decode_response(response)

    def calculate(self, data: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate CURP structure.

        Calculates the structure of a CURP with provided data.

        Args:
            data (dict): Dictionary with required fields:
                - names: First names
                - lastName: Last name (apellido paterno)
                - secondLastName: Second last name (apellido materno)
                - birthDay: Birth day
                - birthMonth: Birth month
                - birthYear: Birth year
                - gender: Gender (H/M)
                - entity: Entity code

        Returns:
            dict: Calculated CURP response

        Raises:
            ValidaCurpException: If token is not set, required data is missing, or API error occurs
            RequestException: If HTTP request fails
        """
        if not self.get_token():
            raise ValidaCurpException("The token was not set")

        if self.get_version() == 1:
            return self._calculate_v1(data)
        else:
            return self._calculate_v2(data)

    def _calculate_v1(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Calculate CURP using API v1."""
        self._validate_data_calculate(data)

        data_v1 = {
            "nombres": data["names"],
            "apellido_paterno": data["lastName"],
            "apellido_materno": data["secondLastName"],
            "dia_nacimiento": data["birthDay"],
            "mes_nacimiento": data["birthMonth"],
            "anio_nacimiento": data["birthYear"],
            "sexo": data["gender"],
            "entidad": data["entity"],
        }

        url = self._make_url("calcular_curp", None, data_v1)
        response = self._request_get(url)
        return self._decode_response(response)

    def _calculate_v2(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Calculate CURP using API v2."""
        self._validate_data_calculate(data)

        # Adjust data for v2 API
        data_v2 = data.copy()
        data_v2["birthday"] = data_v2.pop("birthDay")
        data_v2["yearBirth"] = data_v2.pop("birthYear")

        response = self._make_request("calculateCURP", None, data_v2)
        return self._decode_response(response)

    def _validate_data_calculate(self, data: Dict[str, str]) -> None:
        """Validate required data for calculate method."""
        required_fields = [
            "names", "lastName", "secondLastName",
            "birthDay", "birthMonth", "birthYear",
            "gender", "entity"
        ]

        for field in required_fields:
            if field not in data:
                raise ValidaCurpException(f"The {field} was not set")

    def get_entities(self) -> Dict[str, Any]:
        """
        Get list of entities.

        Returns:
            dict: List of entities response

        Raises:
            ValidaCurpException: If token is not set or API error occurs
            RequestException: If HTTP request fails
        """
        if not self.get_token():
            raise ValidaCurpException("The token was not set")

        if self.get_version() == 1:
            return self._get_entities_v1()
        else:
            return self._get_entities_v2()

    def _get_entities_v1(self) -> Dict[str, Any]:
        """Get entities using API v1."""
        url = self._make_url("entidades")
        response = self._request_get(url)
        return self._decode_response(response)

    def _get_entities_v2(self) -> Dict[str, Any]:
        """Get entities using API v2."""
        response = self._make_request("getEntities")
        return self._decode_response(response)

    def _request_get(self, url: str) -> requests.Response:
        """Make GET request."""
        try:
            response = requests.get(url)
            return response
        except RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                self._decode_response(e.response)
            raise

    def _request_post(self, url: str, data: Dict[str, Any]) -> requests.Response:
        """Make POST request."""
        try:
            response = requests.post(url, json=data)
            return response
        except RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                self._decode_response(e.response)
            raise

    def _decode_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Decode API response.

        Args:
            response: HTTP response object

        Returns:
            dict: Decoded response data

        Raises:
            ValidaCurpException: For API errors
        """
        attr = "error_message" if self.get_version() == 1 else "msn"

        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("response", response_data)
        elif response.status_code in [401, 403]:
            error_data = response.json()
            error_msg = error_data.get(attr, "Authentication failed")
            raise ValidaCurpException(f"Failed authentication: {error_msg}")
        elif response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get(attr, "Bad request")
            raise ValidaCurpException(f"Bad request: {error_msg}")
        else:
            raise ValidaCurpException(f"The request failed: {response.reason}")

    def _make_url(self, method: str, curp: Optional[str] = None,
                  extra_data: Optional[Dict[str, str]] = None) -> str:
        """Build URL for API v1."""
        data = {"token": self.get_token()}

        if curp:
            data["curp"] = curp

        if extra_data:
            data.update(extra_data)

        # Add library information
        data.update({
            "library": self.TYPE,
            "library_version": self.LIBRARY_VERSION,
            "api_version": self.get_version(),
        })

        return f"{self.get_endpoint()}{method}?{urlencode(data)}"

    def _make_request(self, method: str, curp: Optional[str] = None,
                      extra_data: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make request for API v2."""
        data = {"token": self.get_token()}

        if curp:
            data["curp"] = curp

        if extra_data:
            data.update(extra_data)

        # Add library information to query string
        query_params = {
            "library": self.TYPE,
            "library_version": self.LIBRARY_VERSION,
            "api_version": self.get_version(),
        }

        url = f"{self.get_endpoint()}{method}?{urlencode(query_params)}"
        return self._request_post(url, data)


"""
ValidaCurp Exception

Custom exception class for ValidaCurp Client.
"""


class ValidaCurpException(Exception):
    """Custom exception for ValidaCurp operations."""
    pass
