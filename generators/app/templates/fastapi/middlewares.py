<%_ if (jwt) { _%>
import jwt
<%_ } _%>
from fastapi import Depends, HTTPException, Header<%_ if (jwt) { _%>, Security
from fastapi.security import OAuth2PasswordBearer
<%_ } _%>
from starlette.status import HTTP_403_FORBIDDEN
from starlette.requests import Request
from utils import CONFIG
from logzero import logger
<%_ if (jwt) { _%>
from models import TokenPayload
<%_ } _%>


def internal_only(internal_header: str = Header(None)):
    logger.info("ROLE = %s", internal_header)
    if internal_header != 'service':
        raise HTTPException(HTTP_403_FORBIDDEN, detail="Access denied")
<%_ if (jwt) { _%>


# authentication
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/authenticate/login/access-token")
# need to write api with URL '/user/login/access-token' which return a token.


def authenticate_user(
    token: str = Security(reusable_oauth2)
):

    try:
        payload = jwt.decode(token, CONFIG['SECRET_KEY'], algorithms=["HS256"])
        token_data = TokenPayload(**payload)
        return token_data
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
<%_ } _%>


async def connections(conn: dict, request: Request, call_next):
    """Bootstrapping every request with
    connection services
    """
    request.state.conn = conn
    request.state.config = CONFIG

    response = await call_next(request)
    return response


def get_deps(request: Request):
    return request.state.conn


deps = Depends(get_deps)
