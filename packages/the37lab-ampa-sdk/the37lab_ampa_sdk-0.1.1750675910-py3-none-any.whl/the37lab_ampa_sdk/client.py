import os
import requests
from requests.auth import HTTPBasicAuth

class PromptAPI:
    def __init__(self, ampa_url=None, username=None, password=None, api_token=None):
        if ampa_url is None:
            ampa_url = os.getenv("AMPA_API_URL", "https://ampa-api.the37lab.com/")
        if username is None:
            username = os.getenv("AMPA_API_USERNAME")
        if password is None:
            password = os.getenv("AMPA_API_PASSWORD")
        if api_token is None:
            api_token = os.getenv("AMPA_API_TOKEN")
        self.base_url = ampa_url.rstrip('/')
        if username and password:
            self.auth = HTTPBasicAuth(username, password)
            self.api_token = None
        elif api_token:
            self.auth = None
            self.api_token = api_token
        else:
            raise ValueError("Either username and password or api_token must be provided")

    def _get_headers(self):
        if self.api_token:
            return {"X-API-Token": self.api_token}
        return {}

    def create_prompt(self, **kwargs):
        url = f"{self.base_url}/api/v1/prompts"
        response = requests.post(url, params=kwargs, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def list_prompts(self):
        url = f"{self.base_url}/api/v1/prompts"
        response = requests.get(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_prompt(self, prompt):
        url = f"{self.base_url}/api/v1/prompts/{prompt}"
        response = requests.get(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_prompt_versions(self, prompt):
        url = f"{self.base_url}/api/v1/prompts/{prompt}/versions"
        response = requests.get(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def call_prompt(self, prompt, variables=None, prompt=None):
        url = f"{self.base_url}/api/v1/prompts/{prompt}/call"
        params = []
        if variables:
            for k, v in variables.items():
                params.append(('var', f"{k}={v}"))
        if prompt:
            params.append(('prompt', prompt))
        response = requests.post(url, params=params, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def update_prompt(self, prompt_id, **kwargs):
        url = f"{self.base_url}/api/v1/prompts/{prompt_id}/update_prompt"
        response = requests.put(url, params=kwargs, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def delete_prompt(self, prompt_id):
        url = f"{self.base_url}/api/v1/prompts/{prompt_id}"
        response = requests.delete(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def delete_prompt_version(self, prompt_id, version_id):
        url = f"{self.base_url}/api/v1/prompts/{prompt_id}/versions/{version_id}"
        response = requests.delete(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()