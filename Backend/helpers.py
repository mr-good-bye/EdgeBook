from fastapi import Request, HTTPException
from Backend.DbCon.connection import check_token


async def require_token(_req: Request) -> tuple[str, str]:
    if 'token' not in _req.query_params.keys():
        if 'token' not in _req.cookies.keys():
            raise HTTPException(status_code=418, detail="I'm a teapot or you. Provide token")
        else:
            token = _req.cookies.get('token')
    else:
        token = _req.query_params.get('token')
    access = await check_token(token)
    if not access[0]:
        raise HTTPException(status_code=401, detail=access[1])
    return access[1], token
