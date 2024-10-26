from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from ninja import Router
from ninja.errors import HttpError
from ninja_extra import api_controller
from ninja_jwt.controller import TokenObtainPairController

from .schemas import RegisterSchema

router = Router(tags=["user"])


@router.post("/register")
def register(request, payload: RegisterSchema):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username already taken")

    validate_password(payload.password)
    User.objects.create_user(username=payload.username, password=payload.password)
    return {"status": "OK"}


@api_controller("token", tags=["Auth"])
class MyCustomController(TokenObtainPairController):
    """obtain_token and refresh_token only"""
