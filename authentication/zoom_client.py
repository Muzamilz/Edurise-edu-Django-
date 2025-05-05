import requests
from datetime import datetime
from django.conf import settings

class ZoomClient:
    """Client for interacting with the Zoom API."""
    
    def __init__(self, api_key, api_secret, access_token):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.base_url = 'https://api.zoom.us/v2'
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def meetings(self):
        """Return a Meetings instance for managing meetings."""
        return Meetings(self)
    
    def users(self):
        """Return a Users instance for managing users."""
        return Users(self)

class Meetings:
    """Class for managing Zoom meetings."""
    
    def __init__(self, client):
        self.client = client
    
    def create(self, topic, start_time, duration, type=2):
        """Create a new meeting."""
        url = f"{self.client.base_url}/users/me/meetings"
        data = {
            'topic': topic,
            'type': type,
            'start_time': start_time,
            'duration': duration,
            'timezone': 'UTC',
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': False,
                'mute_upon_entry': True,
                'waiting_room': True
            }
        }
        
        response = requests.post(url, headers=self.client.headers, json=data)
        response.raise_for_status()
        return Meeting(response.json())

class Users:
    """Class for managing Zoom users."""
    
    def __init__(self, client):
        self.client = client
    
    def me(self):
        """Get the current user's information."""
        url = f"{self.client.base_url}/users/me"
        response = requests.get(url, headers=self.client.headers)
        response.raise_for_status()
        return response.json()

class Meeting:
    """Class representing a Zoom meeting."""
    
    def __init__(self, data):
        self.id = data['id']
        self.join_url = data['join_url']
        self.start_url = data.get('start_url')
        self.topic = data['topic']
        self.start_time = data['start_time']
        self.duration = data['duration']
        self.timezone = data['timezone']
        self.created_at = data['created_at']
        self.status = data['status'] 