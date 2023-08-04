from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from api.auth.auth_manager import get_user_manager
from api.auth.auth_models import User
from config import SECRET_KEY

bearer_transport = BearerTransport(tokenUrl="/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    _SECRET_KEY = SECRET_KEY
    return JWTStrategy(secret=_SECRET_KEY, lifetime_seconds=3600 * 24 * 15)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(verified=True)
current_superuser = fastapi_users.current_user(verified=True, superuser=True)
unverified_user = fastapi_users.current_user(optional=True)
