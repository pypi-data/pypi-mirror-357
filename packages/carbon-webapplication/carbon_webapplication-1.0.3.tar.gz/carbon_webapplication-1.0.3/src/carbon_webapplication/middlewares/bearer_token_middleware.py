from fastapi import FastAPI,Request
import jwt
from ..enums.header_names import HeaderNames
from ..dtos.user import UserClaims
from ..dtos.request import CarbonBaseRequest, CarbonRoute


BearerTokenClaimMapper = {
    "sub": "ClientId",
    "tenant-id": "TenantId",
    "god-user": "GodUser"
}

async def BearerTokenMiddleware(request: Request, call_next):
    authorization = request.headers.get(HeaderNames.Authorization)

    if authorization:
        bearer_token = authorization.split(" ")[1] if HeaderNames.Bearer in authorization else None
        
        if bearer_token:
            claims = jwt.decode(bearer_token, options={"verify_signature": False})

            # Başlıkları düzenle
            if claims:

                request.state.token = bearer_token
                # "GodUser" başlığını kaldır
                if "GodUser" in request.headers:
                    del request.headers["GodUser"]
                
                # "TenantId" başlığını kaldır
                if claims.get("god-user") != "true":
                    if "TenantId" in request.headers:
                        del request.headers["TenantId"]

                # "ClientId" başlığını kaldır
                if "ClientId" in request.headers:
                    del request.headers["ClientId"]

                # Claim'leri başlıklara ekle
                for claim_type, mapped_key in BearerTokenClaimMapper.items():
                    if claim_type in claims:
                        request.headers.__dict__[mapped_key] = claims[claim_type]
                user = UserClaims(claims=claims)
                request.state.user_claims = user

    response = await call_next(request)
    return response