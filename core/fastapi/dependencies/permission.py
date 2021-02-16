from typing import List

from fastapi import Request
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase

from app.usecases import UserUsecase
from core.exceptions import UnauthorizedException


class PermissionDependency(SecurityBase):
    def __init__(self, permissions: List):
        self.permissions = permissions
        self.model: APIKey = APIKey(**{"in": APIKeyIn.header}, name="Authorization")
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request):
        for permission in self.permissions:
            cls = permission()
            if not await cls.has_permission(request=request):
                raise cls.exception


class IsAuthenticated:
    exception = UnauthorizedException

    async def has_permission(self, request: Request):
        return request.user.id is not None


class IsAdmin:
    exception = UnauthorizedException

    async def has_permission(self, request: Request):
        user_id = request.user.id
        if not user_id:
            return False

        return await UserUsecase().is_admin(user_id=user_id)