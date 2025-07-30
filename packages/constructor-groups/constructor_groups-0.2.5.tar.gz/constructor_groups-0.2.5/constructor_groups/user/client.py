import os
from dotenv import load_dotenv, find_dotenv
load_dotenv()

class UserClient:
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
    
    def upsert_user(self, payload):
        return self._make_request("POST", 'user', payload)
    
    def delete_by_user_id(self, user_id):
        return self._make_request("DELETE", f'user/{user_id}')
    
    def search_user(self, payload):
        return self._make_request("POST", f'user/search', data=payload)
    
    def get_user_by_id(self, user_id):
        return self._make_request("GET", f'user/{user_id}')
    
    def get_user_by_username(self, username):
        return self._make_request("GET", f'user/{username}')