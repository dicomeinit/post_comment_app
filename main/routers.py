from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from posts.routes import router as posts_router
from users.routes import router as users_router

api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)
api.add_router("/users/", users_router)
api.add_router("/posts/", posts_router)
