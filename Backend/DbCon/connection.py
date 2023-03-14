import datetime
import edgedb
import asyncio
from Backend.DbCon import parser
from Backend import constants as const
import bcrypt
import secrets

client = edgedb.create_async_client()


async def connection_check() -> bool:
    hw = await client.query("""
        SELECT VapePuff;
    """)

    await client.aclose()
    if isinstance(hw, list) and len(hw) > 0 and isinstance(hw[0], edgedb.Object):
        return True
    return False


async def get_scheme() -> dict:
    hw = await client.query("""
        describe schema as ddl;
    """)

    res = parser.parse_ddl(hw[0])
    return res


async def login(username: str, password: str):  # TODO: NonUser
    user = await client.query(f"""
        SELECT User{{
            username,
            hash
        }} filter User.username = '{username}';
    """)
    if len(user) == 0:
        return False, 'User not found'
    if len(user) > 1:
        return False, 'Error, multiple users'
    user = user[0]
    return bcrypt.checkpw(password.encode('utf-8'), user.hash.encode('utf-8')), 'Success'


async def create_token(username: str):
    tkns = await client.query(f"""
        SELECT Token{{token}}
    """)
    token = secrets.token_urlsafe()
    while token in tkns:
        token = secrets.token_urlsafe()

    await client.query(f"""
        INSERT Token {{
            token := '{token}',
            created := datetime_current(),
            user := (SELECT User filter .username = '{username}')
        }}
    """)
    return token


async def drop_token(token: str = None):
    qr = await client.query(f"""
        DELETE Token
        filter .token = '{token}'
    """)
    return qr.__len__


async def check_token(token: str):
    qr = await client.query(f"""
        SELECT Token {{
            id,
            created,
            user: {{username}}
        }} filter .token = '{token}';
    """)
    if len(qr) == 0:
        return False, 'Token no longer valid'
    if datetime.datetime.now(datetime.timezone.utc) - qr[0].created > datetime.timedelta(hours=8):
        await drop_token(token)
        return True, qr[0].user.username, '8 hours have expired'
    username = qr[0].user.username
    return True, username


async def register(username, password):
    users = await client.query(f"""
        SELECT User.username
    """)
    nusers = await client.query(f"""
        SELECT NonUser.username
    """)
    if username in users or username in nusers:
        return False, 'Nickname already registered'
    await client.query(f"""
        INSERT NonUser{{
            username := '{username}',
            hash := '{bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')}'
        }}
    """)
    return True, f'Now contact {const.ADMIN_CONTACT} to approve'


async def get_nonusers():
    nusers = await client.query(f"""
        SELECT NonUser{{
            username,
            created
        }}
    """)
    return nusers


async def approve(username: str):
    _ = await client.query(f"SELECT NonUser filter .username = '{username}'")
    if len(await client.query(f"SELECT NonUser filter .username = '{username}'")) == 0:
        return False, 'No such NonUser found'
    nuser = await client.query(f"""
        SELECT NonUser{{
            username,
            hash
        }}
    """)
    await client.query(f"""
        INSERT User{{
            username := '{nuser[0].username}',
            hash := '{nuser[0].hash}'
        }}
    """)
    await client.query(f"DELETE NonUser filter .username = '{nuser[0].username}'")
    return True, nuser[0].username


async def delete_user(username: str):
    if len(await client.query(f"DELETE User filter .username = '{username}'")) == 0:
        return False, "No such user found"
    return True, username

async def test():
    print('Connection Check: ', await connection_check())
    print('Login test: ', await login(*const.TEST_USER))
    token = await create_token(const.TEST_USER[0])
    print('Token check: ', await check_token(token))


if __name__ == "__main__":
    asyncio.run(test())
