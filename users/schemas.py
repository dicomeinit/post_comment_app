from django.contrib.auth.models import User
from ninja import Schema
from ninja.orm import create_schema


class RegisterSchema(Schema):
    username: str
    password: str


class LoginSchema(Schema):
    username: str
    password: str


class LoginResponseSchema(Schema):
    access: str
    refresh: str


UserSchema = create_schema(
    User,
    exclude=[
        "password",
        "last_login",
        "is_superuser",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "date_joined",
        "groups",
        "user_permissions",
    ],
)
