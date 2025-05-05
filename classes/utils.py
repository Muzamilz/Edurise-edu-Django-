from django.conf import settings
import requests
import json
from datetime import datetime, timedelta

def create_zoom_meeting(topic, start_time, duration_minutes=60):
    """
    Create a Zoom meeting using the Zoom API.
    
    Args:
        topic (str): The meeting topic
        start_time (datetime): The meeting start time
        duration_minutes (int): Meeting duration in minutes
    
    Returns:
        dict: Meeting details including join URL and meeting ID
    """
    # Get Zoom API credentials from settings
    api_key = settings.ZOOM_API_KEY
    api_secret = settings.ZOOM_API_SECRET
    
    # Create the meeting payload
    payload = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration": duration_minutes,
        "timezone": "UTC",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "mute_upon_entry": True,
            "waiting_room": True,
        }
    }
    
    # Make the API request to create the meeting
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "https://api.zoom.us/v2/users/me/meetings",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Log the error and return None
        print(f"Error creating Zoom meeting: {str(e)}")
        return None 