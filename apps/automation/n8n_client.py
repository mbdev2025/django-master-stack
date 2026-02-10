import requests
from django.conf import settings

class N8NClient:
    def __init__(self):
        self.base_url = getattr(settings, 'N8N_BASE_URL', '')
        self.api_key = getattr(settings, 'N8N_API_KEY', '')

    def trigger_workflow(self, webhook_path, data):
        url = f"{self.base_url}/webhook/{webhook_path}"
        headers = {"X-N8N-API-KEY": self.api_key}
        return requests.post(url, json=data, headers=headers)
