import os
import requests
from urllib.parse import urlencode
from .session.client import SessionClient
from .user.client import UserClient
from .attendee.client import AttendeeClient
from .report.client import ReportClient
import hashlib

def generate_auth_header(access_key: str, secret_key: str) -> str:
    """
    Generates a hashed Authorization header using access and secret keys.
    Format: Bearer <access>|<sha256(access|secret)>
    """
    raw = f"{access_key}|{secret_key}"
    hash_value = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"Bearer {access_key}|{hash_value}"


def default_success_handler(response):
    return response

class APIClient:
    def __init__(self, success_handler=None):
        self.sessions = SessionClient(self)
        self.users = UserClient(self)
        self.attendees = AttendeeClient(self)
        self.reports = ReportClient(self)
        self.domain = None
        self.success_handler = success_handler or default_success_handler

    def set_domain(self, domain):
        self.domain = domain

    def set_credentials(self, access_key, secret_key, account_id=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.account_id = account_id

    def _make_request(self, method, endpoint, data=None, params=None):
        url = endpoint
        if params:
            query_string = urlencode(params)
            url = f"{url}?{query_string}"
            
        headers = {
            "Authorization": generate_auth_header(self.access_key, self.secret_key),
            "Content-Type": "application/json"
        }

        try:
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            try:
                return {
                    "error": "HTTP error",
                    "status_code": response.status_code,
                    "details": response.json()
                }
            except ValueError:
                return {
                    "error": "HTTP error",
                    "status_code": response.status_code,
                    "details": response.text
                }
        except requests.exceptions.RequestException as e:
            return {
                "error": "Request failed",
                "details": str(e)
            }

        if response.status_code == 204:
            result = None
        else:
            result = response.json()

        self.success_handler(result)
        return result
