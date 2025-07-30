import os
from dotenv import load_dotenv, find_dotenv
load_dotenv()

class ReportClient:
    def __init__(self, client):
        self.client = client
        self.base_url = None

    def _make_request(self, method, endpoint, data=None, params=None):
        env_path = find_dotenv()
        if env_path:
            load_dotenv(env_path)
            self.base_url = os.getenv("GROUPS_XAPI_URL")

        self.base_url = f"https://{self.client.domain}/xapi/v2" if self.client.domain is not None else self.base_url
        url = f'{self.base_url}/{endpoint}'

        return self.client._make_request(method, url, data=data, params=params)

    def get_session_stats(self, session_id):
        return self._make_request("GET", f'report/session/{session_id}')

    def get_session_user_stats(self, session_id):
        return self._make_request("GET", f'report/session/{session_id}/attendees')
    
    def get_session_user_stat_by_email(self, session_id, email):
        return self._make_request("GET", f'report/session/{session_id}/attendee/{email}')
    