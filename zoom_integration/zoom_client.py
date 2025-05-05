from zoomus import ZoomClient
from django.conf import settings

class ZoomClient:
    def __init__(self, api_key=None, api_secret=None, access_token=None):
        self.api_key = api_key or settings.ZOOM_API_KEY
        self.api_secret = api_secret or settings.ZOOM_API_SECRET
        self.access_token = access_token
        self.client = ZoomClient(self.api_key, self.api_secret)

    def meetings(self):
        return self.client.meeting

    def users(self):
        return self.client.user

    def webinars(self):
        return self.client.webinar

    def recordings(self):
        return self.client.recording

    def reports(self):
        return self.client.report 