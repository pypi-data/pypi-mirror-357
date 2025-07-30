import requests
import backoff
import json
import json
from typing import Dict

from typing import Callable, Dict, Optional
from .const import SNAPCHAT_SERVER_URL_LOGIN, SNAPCHAT_SERVER_URL_API


class SnapchatClient:
    def __init__(self, snapchat_credentials: str, _adscale_log: Optional[Callable] = None) -> None:
        with open(snapchat_credentials) as credentials:
            snapchat_credentials = json.load(credentials)
        self._client_id = snapchat_credentials.get('client_id'),
        self._client_secret = snapchat_credentials.get('client_secret')
        self._refresh_token = snapchat_credentials.get('refresh_token')
        self._code = snapchat_credentials.get('code')
        self._access_token = self.get_access_token()  

        if _adscale_log:
            self.log = _adscale_log
        else:
            self.log = print


    @backoff.on_exception(backoff.expo, requests.exceptions.HTTPError, max_tries=5)
    def _make_request(self, endpoint: str, method: str, addBearerTokenAuthorization: bool = True,
        params: Dict = None, headers: Dict = None, **kwargs) -> requests.models.Response:
        """Send a request to Snapchat API"""
        if headers == None and addBearerTokenAuthorization:
            headers={'Authorization': f'Bearer {self._access_token}'}
        response = requests.request(method=method, url=f"{endpoint}", headers=headers, params=params, **kwargs)
        
        if response.status_code == 401:
            self._access_token = self.get_access_token()
            response = requests.request(method=method, url=f"{endpoint}", headers=headers, params=params, **kwargs)

        response.raise_for_status()
        return response

    def get_access_token(self) -> str:
        """Refresh acccess token for Snapchat API
        For more information, please refers to: https://marketingapi.snapchat.com/docs/#refresh-the-access-token
        """
        reponse = self._make_request(
            f"{SNAPCHAT_SERVER_URL_LOGIN}/access_token",
            'POST',
            addBearerTokenAuthorization=False,
            data={
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'refresh_token': self._refresh_token,
                'grant_type': 'refresh_token',
            },
            )
        return reponse.json()['access_token']

    def get_account_details(self, ad_account_id) -> str:
        url = f"{SNAPCHAT_SERVER_URL_API}/adaccounts/{ad_account_id}"
        response = self._make_request(
            url,
            'GET'
            )
        return response.json()['adaccounts']
