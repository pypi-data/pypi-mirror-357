import requests

class CloudHandsBase:
    def __init__(self, api_key=None, access_token=None):
        self.api_key = api_key
        self.access_token = access_token

    def _get_headers(self, is_json=True):
        headers = {}

        if self.api_key:
            headers['X-API-KEY'] = self.api_key
        elif self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        if is_json:
            headers['Content-Type'] = 'application/json'
        return headers

    def _make_request(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        
    def authenticated(self):
        """
        Check if the instance is authenticated.
        Raise an exception if neither API key nor access token is provided.
        """
        if not self.api_key and not self.access_token:
            raise Exception("No API key or access token provided. Please authenticate first.")
        return True