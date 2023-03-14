import requests as r
from Backend import constants as const
import json


class EdgeBookApi:
    def __init__(self, address: str, auth: tuple[str, str] = None, register: bool = False):
        self.username, self.token = None, None
        self.address = address
        _test = r.get(self.address).json()
        if _test['message'] != 'Hello World!':
            raise ConnectionError('No or incorrect connection!')
        if auth:
            self.username = auth[0]
            req = r.get(self.address+'/login', params={
                'username': auth[0],
                'password': auth[1]
            })
            if req.status_code == 200 and req.json()['status'] == 'Success':
                self.token = req.json()['token']
                print(f"{r.get(self.address+'/hello', params={'token':self.token}).json()}")
            else:
                print(f"{req.status_code}: {req.content}")

    def check_db(self):
        req = r.get(self.address+'/database').json()
        return req.status_code, json.loads(req.content)

    def database_scheme(self):
        req = r.get(self.address+'/database/scheme', params={'token': self.token})
        return req.status_code, json.loads(req.content)

    def get_approve_list(self):
        req = r.get(self.address+'/approval/list', params={'token': self.token})
        return req.status_code, json.loads(req.content)

    def approve(self, username):
        req = r.get(self.address+'/approval/approve', params={'token': self.token,
                                                              'username': username})
        return req.status_code, json.loads(req.content)

    def delete_user(self, username):
        req = r.get(self.address+'/users/delete', params={'token': self.token,
                                                          'username': username})
        return req.status_code, json.loads(req.content)

    def exit(self):
        if self.token:
            print("GoodBye!")
            req = r.get(self.address+'/logout', params={'token': self.token})

    @staticmethod
    def register(address: str, auth: tuple[str, str]):
        req = r.get(address+'/register', params={
            'username': auth[0],
            'password': auth[1]
        })
        return req.status_code, json.loads(req.content)


if __name__ == "__main__":
    eba = EdgeBookApi('http://127.0.0.1:8000', auth=const.TEST_USER)

    print(EdgeBookApi.register('http://127.0.0.1:8000', ('tulala', 'Pistryun')))
    print(eba.get_approve_list())
    print(eba.approve('tulala'))
    print(eba.get_approve_list())

    EdgeBookApi('http://127.0.0.1:8000', ('tulala', 'Pistryun')).exit()

    print(eba.delete_user('tulala'))

    eba.exit()
