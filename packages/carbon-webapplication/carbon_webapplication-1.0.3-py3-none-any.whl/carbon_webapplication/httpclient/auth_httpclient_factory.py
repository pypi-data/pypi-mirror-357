import requests
import yaml
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union

class AuthenticationType:
    BasicAuth = 0
    OAuth2 = 1
    OneM2MSpecific = 2
    OneM2MConnector = 3
    OAuthClientCredentials = 4

class AuthenticationInfo:
    def __init__(self, primary_access_id: str, primary_access_id_expire_date: Optional[datetime], name: str):
        self.auth_type = None
        self.primary_access_id = primary_access_id
        self.primary_access_id_expire_date = primary_access_id_expire_date
        self.name = name

class BasicAuth(AuthenticationInfo):
    def __init__(self, access_token: str, access_token_expiry_date: Optional[datetime], name: str):
        super().__init__(access_token, access_token_expiry_date, name)
        self.access_token = access_token
        self.access_token_expiry_date = access_token_expiry_date
        self.auth_type = AuthenticationType.BasicAuth

class OneM2MAuth(AuthenticationInfo):
    def __init__(self, application_entity_id: str, application_entity_id_expiry_date: Optional[datetime], name: str):
        super().__init__(application_entity_id, application_entity_id_expiry_date, name)
        self.application_entity_id = application_entity_id
        self.application_entity_id_expiry_date = application_entity_id_expiry_date
        self.auth_type = AuthenticationType.OneM2MSpecific

class AuthHttpClientFactory:
    def __init__(self, config_file: Union[str, Dict[str, Any]]):
        self.config = self.load_config(config_file)
        self.authentications = {}
        self.current_session_headers = {}

    def load_config(self, config_file: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        if config_file is Dict[str, Any]: return config_file
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def drop_authentication(self, name: str) -> bool:
        if name in self.authentications:
            del self.authentications[name]
            return True
        return False

    def re_authenticate(self, name: str) -> Optional[AuthenticationInfo]:
        self.drop_authentication(name)
        return self.create_authentication(name)

    def create_authentication(self, name: str, reauth: bool = False) -> Optional[AuthenticationInfo]:
        if not reauth:
            if name in self.authentications and self.authentications[name].primary_access_id_expire_date > datetime.now():
                return self.authentications[name]

        related_section = self.config.get("Authorizations", {}).get(name)
        if not related_section or not related_section.get("AuthenticationType"):
            return None

        auth_type = int(related_section["AuthenticationType"])

        if auth_type == AuthenticationType.BasicAuth:
            credentials = {
                "username": related_section["UserName"],
                "password": related_section["Password"],
                "scope": related_section["Scope"],
                "client_id": related_section["ClientId"],
                "client_secret": related_section["Secret"]
            }
            token_response = requests.post(
                self.config["JwtSettings"]["Authority"] + "/connect/token",
                data={
                    "grant_type": "password",
                    "username": credentials["username"],
                    "password": credentials["password"],
                    "scope": credentials["scope"],
                    "client_id": credentials["client_id"],
                    "client_secret": credentials["client_secret"]
                }
            )

            if token_response.ok:
                data = token_response.json()
                acc_token = data["access_token"]
                basic_auth = BasicAuth(acc_token, datetime.now() + timedelta(seconds=data["expires_in"]), name)
                self.authentications[name] = basic_auth
                return basic_auth
            else:
                raise Exception("Identity server authentication error: " + str(token_response.status_code))

        elif auth_type == AuthenticationType.OAuthClientCredentials:
            credentials = {
                "client_id": related_section["ClientId"],
                "client_secret": related_section["Secret"],
                "scope": related_section["Scope"]
            }
            token_response = requests.post(
                self.config["JwtSettings"]["Authority"] + "/connect/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": credentials["client_id"],
                    "client_secret": credentials["client_secret"],
                    "scope": credentials["scope"]
                }
            )

            if token_response.ok:
                data = token_response.json()
                authentication_info = BasicAuth(data["access_token"], datetime.now() + timedelta(seconds=data["expires_in"]), name)
                self.authentications[name] = authentication_info
                return authentication_info
            else:
                raise Exception("Identity server authentication error: " + token_response.json().get('error'))

        elif auth_type == AuthenticationType.OneM2MSpecific:
            aeid = related_section["ApplicationEntityId"]
            one_m2m_auth = OneM2MAuth(aeid, datetime.max, name)
            one_m2m_auth.fqdn = related_section["FQDN"]
            self.authentications[name] = one_m2m_auth
            return one_m2m_auth

        return None

    def get_authentication(self, name: str) -> Optional[AuthenticationInfo]:
        if name in self.authentications and self.authentications[name].primary_access_id_expire_date > datetime.now():
            return self.authentications[name]
        return self.re_authenticate(name)

    def get_auth_names(self) -> list:
        return list(self.authentications.keys())

    def send_request(self, name: str, request: requests.Request) -> requests.Response:
        client = requests.Session()
        auth_info = self.get_authentication(name)

        if auth_info and auth_info.auth_type == AuthenticationType.BasicAuth:
            client.headers['Authorization'] = f'Bearer {auth_info.primary_access_id}'
        
        response = client.send(request)

        if response.status_code == 401:
            self.re_authenticate(name)
            client.headers['Authorization'] = f'Bearer {auth_info.primary_access_id}'
            response = client.send(request)

        return response