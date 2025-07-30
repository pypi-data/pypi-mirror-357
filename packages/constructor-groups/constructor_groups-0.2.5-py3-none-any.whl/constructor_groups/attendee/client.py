import os
from dotenv import load_dotenv, find_dotenv
load_dotenv()

class AttendeeClient:
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
    
    def add_by_user_id(self, session_id, user_id, role=None):
        if role is None:
            return self.upsert_attendee(session_id, {
                "user_guid": user_id,
            })
        else:
            return self.upsert_attendee(session_id, {
                "user_guid": user_id,
                "role": role
            })
        
    def upsert_attendee(self, session_id, attendee):
        return self.upsert_attendees(session_id, [attendee])
    
    def upsert_attendees(self, session_id, attendees):
        return self._make_request("POST", f'session/{session_id}/attendee/batch', attendees)
    
    def get_by_attendance_code(self, session_id, attendance_code):
        return self._make_request("GET", f'session/{session_id}/attendee/{attendance_code}')
    
    def search_attendees(self, session_id, params):
        return self._make_request("POST", f'session/{session_id}/attendee/search', params)
    
    def get_by_email(self, session_id, email):
        return self._make_request("GET", f'session/{session_id}/attendee/{email}')
    
    def get_by_user_guid(self, session_id, user_guid):
        return self._make_request("GET", f'session/{session_id}/attendee/{user_guid}')

    def delete_by_attendance_code(self, session_id, attendance_code):
        return self._make_request("DELETE", f'session/{session_id}/attendee/{attendance_code}')
    
    def delete_by_user_id(self, session_id, user_id):
        return self._make_request("DELETE", f'session/{session_id}/attendee/{user_id}')
    
    def delete_by_email(self, session_id, email):
        return self._make_request("DELETE", f'session/{session_id}/attendee/{email}')

    
    