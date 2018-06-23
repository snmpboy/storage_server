import requests
import json
import os

username = "mickey"

password = "disneyc4me"


class session:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {"Content-Type": 'application/json'}

    def post(self, url, payload):
        self.session.headers.update(self.headers)
        response = self.session.post(url, data=payload)
        return response

    def put(self, url, f):
        file = open(f, 'rb')
        content = file.readlines()
        filename = os.path.basename(f)
        self.session.headers.update(self.headers)
        self.session.headers.update({'Content-Length': str(len(content)), 'Content-Type': 'application/octet-stream'})
        response = self.session.post(url, data={filename: content})
        return response

    def get(self, url, params=None):
        if params:
            response = self.session.get(url, params=params)
            return response
        else:
            response = self.session.get(url)
            return response

    def delete(self, url, data):
        self.session.headers.update({'Content-Type': 'application/json'})
        response = self.session.delete(url, data=data)
        return response


sess = session()


def login():
    data = json.dumps({'username': username, 'password': password})
    r = sess.post('http://127.0.0.1:5000/login', data)
    if r.text:
        sess.headers.update({'X-Session': r.headers['X-Session'], 'UserId': r.headers['UserId']})
        print(r.text)
    else:

        print(r.status_code)


def register(username=username, password=password):
    data = json.dumps({'username': username, 'password': password})

    r = sess.post('http://127.0.0.1:5000/register', data)
    if r.text:
        print(r.text)
    else:
        print(r.status_code)


def download_file():
    f = input("Enter the name of a file:  ")
    data = {'filename': f}
    r = sess.get('http://127.0.0.1:5000/files', params=data)
    if r.text:
        print(r.text)
    else:
        print(r.status_code)


def list_files():
    r = sess.get('http://127.0.0.1:5000/files')
    print(r.text)


def delete_file():
    f = input("Enter file to delete:  ")
    data = json.dumps({'filename': f})
    r = sess.delete('http://127.0.0.1:5000/files', data)
    if r.text:
        print(r.text, r.status_code)
    else:
        print(r.status_code)


def upload_file():
    path = input("Enter complete path to file (if not in current directory):  ")
    try:
        r = sess.put('http://127.0.0.1:5000/files', path)
        if r.text:
            print(r.text)
        else:
            print(r.status_code)
    except Exception as e:
        print(e)


def main():
    choice = True

    while choice:
        print("""
                1. Register
                2. Login
                3. Upload File
                4. List File(s)
                5. Download File
                6. Delete File
                7. Exit/Quit
            """)
        try:
            choice = int(input("Make a selection:  "))
        except ValueError:
            print("You  must enter an number.")
            continue
        if int(choice) > 7:
            print("Enter a number from 1 to 7'")
            continue
        if choice == 1:
            register()
        if choice == 2:
            login()
        if choice == 3:
            upload_file()
        if choice == 4:
            list_files()
        if choice == 5:
            download_file()
        if choice == 6:
            delete_file()
        if choice == 7:
            choice = False


if __name__ == '__main__':
    main()