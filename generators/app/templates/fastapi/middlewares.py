import jwt

from fastapi import Depends, HTTPException, Header, Security
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_403_FORBIDDEN
from starlette.requests import Request
from utils import CONFIG
from logzero import logger
from models import TokenPayload


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


async def connections(request: Request, call_next):
    """Bootstrapping every request with
    connection services
    """
    conn = {
        'redis': 'redis-class',
        'cass': 'cassandra-class',
        'postgesql': 'postgesql-class'
    }

    request.state.conn = conn
    request.state.config = CONFIG

    response = await call_next(request)
    return response


def get_deps(request: Request):
    return request.state.conn


deps = Depends(get_deps)
