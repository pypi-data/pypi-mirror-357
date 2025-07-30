import random
import requests
import string

from .utils import generate_code_challenge, generate_random_string
from .base import CloudHandsBase
from .sdk_types import ChargeType, CloudhandsPostRequest, CloudhandsPurchaseResult, TransactionState, CloudhandsTransaction, CloudhandsPost
from .version import __version__

# Define your fixed API endpoints here.
API_ENDPOINT = "https://api.cloudhands.ai/"
# API_ENDPOINT = "http://api.localhost:5000"
AUTHORIZATION_URL = "https://cloudhands.ai/auth"
CDN_URL = "https://cdn.cloudhands.ai/"
SDK_VERSION = f"{__version__}-py"  # Use the centralized version from __init__.py

class CloudHands(CloudHandsBase):
    """
    CloudHands General SDK
    """
    def get_user_id(self, username: str) -> str:
        """
        Retrieves the user ID for a given username.

        :param username: The username to look up.
        :return: The user ID associated with the username.
        """
        url = f"{API_ENDPOINT}/userid/{username}"
        headers = self._get_headers()

        try:
            self.authenticated()
            return self._make_request("GET", url, headers=headers)
        except requests.RequestException as e:
            raise Exception(f"Error while retrieving user ID: {str(e)}")

    def get_posts(self, user_id: str, first_item: int = 0) -> list[CloudhandsPost]:
        """
        Retrieves posts for a given user ID.

        :param user_id: The user ID to look up.
        :param first_item: The index of the first item to retrieve.
        :return: A list of CloudhandsPost objects associated with the user ID.
        """
        url = f"{API_ENDPOINT}/posts?userid={user_id}&firstitem={first_item}"
        headers = self._get_headers()

        try:
            self.authenticated()
            posts_data = self._make_request("GET", url, headers=headers).get('posts', [])   
            return [CloudhandsPost(**post) for post in posts_data]
        except requests.RequestException as e:
            raise Exception(f"Error while retrieving posts: {str(e)}")
        
    def like_post(self, post_id: str) -> bool:
        """
        Likes a post by its ID.

        :param post_id: The ID of the post to like.
        :return: True if the post was successfully liked, otherwise False.
        """
        url = f"{API_ENDPOINT}/post/like?id={post_id}"
        headers = self._get_headers()

        try:
            self.authenticated()
            self._make_request("POST", url, headers=headers)
            return True
        except requests.RequestException as e:
            raise Exception(f"Error while liking post: {str(e)}")

    def text_post(self, title: str, content: str):
        """
        Creates a new post with the given title and content.

        :param title: The title of the post.
        :param content: The content of the post.
        :return: The ID of the newly created post.
        """
        url = f"{API_ENDPOINT}/post"
        headers = self._get_headers()
        payload = CloudhandsPostRequest(
            title=title,
            message=content,
        )

        try:
            self.authenticated()
            self._make_request("POST", url, json=payload.__dict__, headers=headers)
        except requests.RequestException as e:
            raise Exception(f"Error while creating post: {str(e)}")
        
    def image_post(self, title: str, content: str, image_path: str):
        """
        Creates a new post with the given title, content, and image.

        :param title: The title of the post.
        :param content: The content of the post.
        :param image_path: The path to the image file.
        :return: The ID of the newly created post.
        """
        url = f"{API_ENDPOINT}/post"
        headers = self._get_headers()

        try:
            self.authenticated()
            # Upload the image first - url is returned in the first element of the list under the key message
            image_url = CDN_URL + self.upload_image(image_path=image_path).get("message", [None])[0]
            payload = CloudhandsPostRequest(
                title=title,
                message=content,
                images= [{ 'url': image_url }]
            )

            return self._make_request("POST", url, json=payload.__dict__, headers=headers)
        except requests.RequestException as e:
            raise Exception(f"Error while creating post: {str(e)}")

    def upload_image(self, image_path: str):
        """
        Uploads an image to the CloudHands server.

        :param image_path: The path to the image file.
        :return: The URL of the uploaded image.
        """
        url = f"{API_ENDPOINT}/post/upload_image"
        headers = self._get_headers(is_json=False)  # Set is_json to False for file upload

        try:
            self.authenticated()
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                return self._make_request("POST", url, files=files, headers=headers)
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except requests.RequestException as e:
            raise Exception(f"Error while uploading image: {str(e)}")
        
    def set_access_token(self, access_token: str):
        """
        Set the access token for the SDK.

        :param access_token: The access token to set.
        """
        self.access_token = access_token
    
    def set_api_key(self, api_key: str):
        """
        Set the API key for the SDK.

        :param api_key: The API key to set.
        """
        self.api_key = api_key

"""
CloudHands SDK Payment Processing:
    - Charge events to the payment_key.
    - Retrieves stats about the payment_key account.
"""
class CloudHandsPayment(CloudHandsBase):
    """
    :param author_key: The Payment Key we will pay.
        - An author can use different keys for different apps, and thus identify which payments come from which apps.
    """
    def __init__(self, author_key: str):
        super().__init__()
        self.author_key = author_key

        # generate random 16 char string for state
        # This is used to prevent CSRF attacks during the OAuth flow.
        self.state = generate_random_string(16, 16)

        # generate random 43-128 char string for code_verifier
        # This is used to securely exchange the authorization code for an access token.
        self.code_verifier = generate_random_string(43, 128)

    def get_authorization_url(self):
        """
        Returns the authorization URL for the user to authenticate and authorize the app.
        The user will be redirected to this URL to grant permissions.

        :return: str - The authorization URL.
        """
        # Generate the code challenge from the code verifier
        code_challenge = generate_code_challenge(self.code_verifier)
        return f"{AUTHORIZATION_URL}?response_type=code&client_id={self.author_key}&redirect_uri=no&state={self.state}&code_challenge={code_challenge}&code_challenge_method=S256"
    
    def exchange_code_for_token(self, code: str):
        """
        Exchanges the authorization code for an access token.

        :param code: The authorization code received after user authentication.
        :return: bool - True if the token was successfully retrieved, otherwise False.
        """
        url = f"{API_ENDPOINT}/token"
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            "clientId": self.author_key,
            "code": code,
            "redirectUri": "no",
            "code_Verifier": self.code_verifier,
        }
        try:
            response = self._make_request("POST", url, json=payload, headers=headers)
            self.access_token = response.get("access_token")
            return True
        except requests.RequestException as e:
            raise Exception(f"Error while exchanging code for token: {str(e)}")

    def cli_authorize(self):
        """
        Authorize the user payment via cli - for now, provide the authorization URL to the user and await their input of the code
        """
        auth_url = self.get_authorization_url()
        print(f"Please visit this URL to authorize the app: {auth_url}")
        print("After authorizing, please enter the code you received:")
        code = input("Code: ")
        if self.exchange_code_for_token(code):
            print("Access token retrieved successfully!")
        else:
            print("Failed to retrieve access token. Please check the code and try again.")


    def charge(self, charge: int, event_name: str = None, charge_type: ChargeType = ChargeType.Each, metadata: dict = None) -> CloudhandsPurchaseResult:
        """
        Sends a charge to the payment_key.
        Both author_key and payment_key are passed along.

        :param charge: Amount to charge for this function.
        :param event_name: (optional) A string identifying the event (e.g. 'user_login', 'purchase_made', etc.).
        :param metadata:   (optional) A dictionary containing additional event metadata 
                           (e.g. user_id, amount). Defaults to empty dict if not provided.
        :return:           (isSuccessful, errors)
                           isSuccessful: bool - True if request returned a 200 status, otherwise False
                           errors: list  - A list of error messages (empty if no errors)
        """
        if metadata is None:
            metadata = {}

        payload = {
            "author_id": self.author_key,
            "sdk_version": SDK_VERSION,
            "charge_type": charge_type.value,
            "charge": charge,
            "event_name": event_name,
            "metadata": metadata,
        }

        url = f"{API_ENDPOINT}/sdk/charge"
        headers = self._get_headers()

        try:
            self.authenticated()
            response = self._make_request("POST", url, json=payload, headers=headers)
            is_successful = response.get("isSuccessful", False)
            transaction_id = response.get("message", {}).get("transaction_id")
            
            return CloudhandsPurchaseResult(
                is_successful=is_successful,
                errors=[],
                transaction_id=transaction_id
            )
        except requests.RequestException as e:
            return CloudhandsPurchaseResult(
                is_successful=False,
                errors=[str(e)]
            )

    def complete_cloudhands_transaction(self, transaction_id: str, charge: int) -> CloudhandsPurchaseResult:
        """
        Complete an escrowed transaction by charging the specified amount.
        
        :param transaction_id: The ID of the transaction to complete.
        :param charge: The amount to charge for this transaction.
        :return: A CloudhandsPurchaseResult object indicating success or failure.
        """
        url = f"{API_ENDPOINT}/sdk/charge/confirm"
        headers = self._get_headers()
        payload = {
            "transaction_id": transaction_id,
            "charge": charge,
        }

        try:
            self.authenticated()
            response = self._make_request("POST", url, json=payload, headers=headers)
            print("Response from complete_cloudhands_transaction:", response)
            is_successful = response.get("isSuccessful", False)
            errors = response.get("errors", [])
            transaction_id = response.get("message", {}).get("transaction_id")

            return CloudhandsPurchaseResult(
                is_successful=is_successful,
                errors=errors,
                transaction_id=transaction_id
            )
        except requests.RequestException as e:
            return CloudhandsPurchaseResult(
                is_successful=False,
                errors=[str(e)]
            )

    def get_transaction(self, transaction_id: str) -> CloudhandsTransaction:
        """
        Retrieves transaction details from the /sdk/transaction API.

        :param transaction_id: The ID of the transaction to retrieve.
        :return: A CloudhandsTransaction object containing the transaction details.
        """
        url = f"{API_ENDPOINT}/sdk/transaction/{transaction_id}"
        headers = self._get_headers()

        try:
            self.authenticated()
            response = self._make_request("GET", url, headers=headers)
            message = response.get("message", {})
            return CloudhandsTransaction(
                author_id=message.get("authorId"),
                user_id=message.get("userId"),
                amount=message.get("amount"),
                type=message.get("type"),
                date=message.get("date"),
                description=message.get("description"),
                processed=message.get("processed"),
                process_state=TransactionState.__members__.get(message.get("processState"), None)
            )
        except requests.RequestException as e:
            raise Exception(f"Error while retrieving transaction: {str(e)}")