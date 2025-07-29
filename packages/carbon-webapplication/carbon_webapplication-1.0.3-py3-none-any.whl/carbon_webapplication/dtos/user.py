from typing import Optional

class UserClaims():
    def __init__(self, claims):
        self._claims = claims  # Gizli bir değişken tanımlıyoruz

    @property
    def claims(self):
        return self._claims

    @claims.setter
    def claims(self, value):
        self._claims = value  # Setter ile değeri değiştirebiliyoruz
    
    def get_user_id(self) -> Optional[str]:
        return self.claims.get('sub')

    def get_user_full_name(self) -> Optional[str]:
        return self.claims.get('fullname')

    def get_user_name(self) -> Optional[str]:
        return self.claims.get('name') or self.get_user_full_name()

    def get_tenant_id(self) -> Optional[str]:
        return self.claims.get('TenantId') or self.claims.get('tenant-id')

    def get_organization_id(self) -> Optional[str]:
        return self.claims.get('OrganizationId') or self.claims.get('organization-id')


    def check_if_god_user(self) -> bool:
        is_god_user = self.claims.get('GodUser') or self.claims.get('god-user')
        return is_god_user is not None and is_god_user.lower() == 'true'