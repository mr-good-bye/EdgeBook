import fastapi
from fastapi import FastAPI, Request, Cookie, Response
from Backend.DbCon import connection as db
import Backend.helpers as hlp


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World!"}


@app.get("/hello/{name}")
async def hello(name: str, resp: Response):
    resp.set_cookie(key='name', value=name)
    return {"message": f"Hello, {name}!"}


@app.get("/hello")
async def hello(_req: Request):
    username, _ = await hlp.require_token(_req)
    return {'message': f"Hello, {username}!"}


@app.get("/database")
async def database():
    database_working = await db.connection_check()
    return {"message": "Database status",
            "connection": database_working}


@app.get("/echo")
async def echo(_a: Request, _ck=Cookie(default=None)):
    ck = dict(_a.cookies)
    a = dict(_a.query_params)
    return {
        "message": "Data echo",
        "data": a,
        "cookies": ck
    }


@app.get("/database/scheme")
async def db_scheme(_req: Request):
    await hlp.require_token(_req)
    res = await db.get_scheme()
    return {
        "message": "Database Scheme",
        "scheme": res
    }


@app.get("/login")
async def login(_req: Request, _res: Response):
    """
    :param _res: Response to set cookies
    :param _req: username and password
    :return: token/not_approved/not_authorised {'status', 'token'}
    """
    data = dict(_req.query_params)
    if 'username' not in data or 'password' not in data:
        raise fastapi.HTTPException(status_code=418, detail="I'm a teapot or you. Provide username and password!")
    user = await db.login(data['username'], data['password'])
    if user[0]:
        _tkn = await db.create_token(data['username'])
        _res.set_cookie(key='token', value=_tkn)
        return {'status': 'Success',
                'token': _tkn,
                'message': user[1]}
    else:
        return {'status': 'Error',
                'token': None,
                'message': user[1]}


@app.get('/logout')
async def logout(_req: Request):
    _, token = await hlp.require_token(_req)
    await db.drop_token(token)


@app.get('/register')
async def register(_req: Request):
    data = dict(_req.query_params)
    if 'username' not in data or 'password' not in data:
        raise fastapi.HTTPException(status_code=418, detail="I'm a teapot or you. Provide username and password!")
    res = await db.register(data['username'], data['password'])
    if res[0]:
        return {'status': 'Success',
                'message': res[1]}
    else:
        raise fastapi.HTTPException(status_code=418, detail=res[1])


@app.get('/approval/list')
async def get_approve(_req: Request):
    _ = await hlp.require_token(_req)
    return {'status': 'Success',
            'message': 'List of NonUsers',
            'list': await db.get_nonusers()}


@app.get('/approval/approve')
async def approval(_req: Request):
    _ = await hlp.require_token(_req)
    data = dict(_req.query_params)
    username = data.get('username')
    if not username:
        raise fastapi.HTTPException(status_code=418, detail='No Username provided')
    res = await db.approve(username)
    if not res[0]:
        raise fastapi.HTTPException(status_code=418, detail=res[1])
    else:
        return {'status': 'Success',
                'message': f'Approved user {res[1]}'}


@app.get('/users/delete')
async def delete_user(_req: Request):
    _ = await hlp.require_token(_req)
    data = dict(_req.query_params)
    username = data.get('username')
    if not username:
        raise fastapi.HTTPException(status_code=418, detail='No Username provided')
    res = await db.delete_user(username)
    if not res[0]:
        raise fastapi.HTTPException(status_code=418, detail=res[1])
    return {'status': 'Success',
            'message': f'Deleted user {res[1]}'}
