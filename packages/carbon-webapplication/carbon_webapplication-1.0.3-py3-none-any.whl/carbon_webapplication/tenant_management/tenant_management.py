import httpx
import yaml
import json
import requests
from typing import List, Optional, Dict, Any, Union
from ..dtos.permission import PermissionDetailedDto,PermissionDetailedFilterDto

class ExternalService:
    def __init__(self, config_file: str):
        self.config = self.load_config(config_file)
        self._policyv2_url = self.config.get("PolicyServerUrlv2", {})

    def load_config(self, config_file: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(config_file, dict): return config_file
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
        
    async def execute_in_policy_api_get_roles(self, filter: PermissionDetailedFilterDto, token: str) -> Optional[List[PermissionDetailedDto]]:
        headers = {'Accept': 'application/json'}

        url = f"{self._policyv2_url}policies/endpoint-item-permissions-with-policies/{filter.user_id}"
        json_data = json.dumps(filter.__dict__)
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(url, headers=headers, params=json_data)

            if response.is_success:
                resp_obj = response.json().get("Data", [])
                return [PermissionDetailedDto.from_dict(item) for item in resp_obj]

            return None
