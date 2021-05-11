import json
import logging
import os
import uuid

import requests
from d3a_interface.constants_limits import JWT_TOKEN_EXPIRY_IN_SECS
from d3a_interface.utils import RepeatingTimer


def retrieve_jwt_key_from_server(domain_name):
    resp = requests.post(
        f"{domain_name}/api-token-auth/",
        data=json.dumps({"username": os.environ["API_CLIENT_USERNAME"],
                         "password": os.environ["API_CLIENT_PASSWORD"]}),
        headers={"Content-Type": "application/json"})
    if resp.status_code != 200:
        logging.error(f"Request for token authentication failed with status "
                      f"code {resp.status_code}."
                      f"Response body: {resp.text}")
        return

    return resp.json()["token"]


def get_request(endpoint, data, jwt_token):
    resp = requests.get(
        endpoint,
        data=json.dumps(data),
        headers={"Content-Type": "application/json",
                 "Authorization": f"JWT {jwt_token}"})
    return resp.json() if request_response_returns_http_2xx(endpoint, resp) else None


def post_request(endpoint, data, jwt_token):
    resp = requests.post(
        endpoint,
        data=json.dumps(data),
        headers={"Content-Type": "application/json",
                 "Authorization": f"JWT {jwt_token}"})
    return resp.json() if request_response_returns_http_2xx(endpoint, resp) else None


def request_response_returns_http_2xx(endpoint, resp):
    if 200 <= resp.status_code <= 299:
        return True
    else:
        logging.error(f"Request to {endpoint} failed with status code {resp.status_code}. "
                      f"Response body: {resp.text}")
        return False


class RestCommunicationMixin:

    def _create_jwt_refresh_timer(self, sim_api_domain_name):
        self.jwt_refresh_timer = RepeatingTimer(
            JWT_TOKEN_EXPIRY_IN_SECS - 30, self._refresh_jwt_token, [sim_api_domain_name]
        )
        self.jwt_refresh_timer.daemon = True
        self.jwt_refresh_timer.start()

    def _refresh_jwt_token(self, domain_name):
        self.jwt_token = retrieve_jwt_key_from_server(domain_name)

    @property
    def _url_prefix(self):
        return f'{self.domain_name}/external-connection/api/{self.simulation_id}'

    def _post_request(self, endpoint_suffix, data):
        endpoint = f"{self._url_prefix}/{endpoint_suffix}/"
        return post_request(endpoint, data, self.jwt_token)

    def _get_request(self, endpoint_suffix, data):
        endpoint = f"{self._url_prefix}/{endpoint_suffix}"
        return get_request(endpoint, data, self.jwt_token)
