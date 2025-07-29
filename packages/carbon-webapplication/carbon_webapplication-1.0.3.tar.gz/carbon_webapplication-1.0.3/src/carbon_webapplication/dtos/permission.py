from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid

class PermissionGroupImpactLevel(Enum):
    User = 1
    OnlyPolicyItself = 2
    PolicyItselfAndItsChildPolicies = 3
    AllPoliciesIncludedInZone = 4

class PermissionType(Enum):
    EndpointItem = 1
    MenuItem = 2
    UIItem = 3 

class PermissionDetailedFilterDto:
    def __init__(self,
                 user_id: Optional[str] = None,
                 solution_id: Optional[str] = None,
                 tenant_id: Optional[str] = None,
                 user_policy_id: Optional[str] = None,
                 permission_names: Optional[List[str]] = None):
        self.user_id = user_id
        self.solution_id = solution_id
        self.tenant_id = tenant_id
        self.user_policy_id = user_policy_id
        self.permission_names = permission_names or []

class PermissionDetailedDto:
    def __init__(self, id: str, name: str, permission_type: Optional[PermissionType], 
                 permission_group_id: str, permission_group_name: str, 
                 privilege_level_type: Optional[PermissionGroupImpactLevel], 
                 privilege_effect_level: Optional[int], user_id: str, 
                 role_id: str, originated_role_type: int, 
                 role_type: int, policies: List[str]):
        self.id = id
        self.name = name
        self.permission_type = permission_type  # Optional
        self.permission_group_id = permission_group_id
        self.permission_group_name = permission_group_name
        self.privilege_level_type = privilege_level_type
        self.privilege_effect_level = privilege_effect_level  # Optional
        self.user_id = user_id
        self.role_id = role_id
        self.originated_role_type = originated_role_type
        self.role_type = role_type
        self.policies = policies

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        permission_type = (
            PermissionType[data['PermissionType']] if 'PermissionType' in data and data['PermissionType'] in PermissionType.__members__
            else None
        )
        privilege_level_type = (
            PermissionGroupImpactLevel[data['PrivilegeLevelType']] if 'PrivilegeLevelType' in data and data['PrivilegeLevelType'] in PermissionGroupImpactLevel.__members__
            else None
        )

        return cls(
            id=data['Id'],
            name=data['Name'],
            permission_type=permission_type,
            permission_group_id=data['PermissionGroupId'],
            permission_group_name=data['PermissionGroupName'],
            privilege_level_type=privilege_level_type,
            privilege_effect_level=data.get('PrivilegeEffectLevel'),
            user_id=data['UserId'],
            role_id=data['RoleId'],
            originated_role_type=data['OriginatedRoleType'],
            role_type=data['RoleType'],
            policies=data.get('Policies', [])
        )