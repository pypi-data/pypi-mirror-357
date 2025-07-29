from fastapi import  Request,Response
from typing import Optional
from fastapi.routing import APIRoute
from typing import Callable, List

from ..dtos.user import UserClaims

class CarbonBaseRequest(Request):
    @property
    def user_claims(self) -> Optional[UserClaims]:
        return getattr(self.state, 'user_claims', None)

    @user_claims.setter
    def user_claims(self, value: UserClaims) -> None:
        self.state.user_claims = value

class CarbonRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: CarbonBaseRequest) -> Response:
            request = CarbonBaseRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler