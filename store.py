from flask import Flask, request
import random
import string
import json
app = Flask(__name__)

USERS = {}


class DataStore:
    """simple in-memory filestore, fix bugs as needed"""
    def __init__(self):
        self.users = {}
        self.user_files = {}

    def get_user_creds(self, user):
        """gets a users credentials from the data store"""
        return self.users.get(user, None)

    def put_user_credentials(self, user, cred):
        """saves a users credentials to the data store"""
        self.users[user] = cred

    def get_user_file(self, user, filename):
        """gets a users file by name, returns None if user or file doesn't exist"""
        files = db.user_files.items()
        new_dict = dict(files)
        for file in new_dict[user]:
            for k, v in file.items():
                if k == filename:
                    return v
        #if this far file doesn't exits
        return None


    def put_user_file(self, user, filename, data):
        """stores file data for user/file"""
        self.user_files.setdefault(user, []).append({filename: data})

    def delete_user_file(self, user, filename):
        """delete a users file"""
        files = db.user_files.items()
        new_dict = dict(files)
        for file in new_dict[user]:
            for k, v in file.items():
                if k == filename:
                    new_dict[user].remove(file)
                    return True

        # if this far file doesn't exits
        return None


db = DataStore()


@app.route('/register', methods=['POST'])
def register():
    """register a user with username and password"""

    if not request.is_json:
        return('', 400)

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username is not None and \
       password is not None and \
       USERS.get(username, None) is None and \
       len(username) > 3 and len(username) < 20 and \
       str(username).isalnum() and \
       len(password) >= 8:
       USERS[username] = password

    if username is None or password is None:
        return ('Both a username and password must be provided.', 400)
    if not str(username).isalnum():
        return ("Username must be alphanumeric with one character.", 400)
    if len(username) < 3 or len(username) > 20:
        return ("Username must be longer than 3 letters and less then 20.", 400)
    if len(password) < 8:
        return ("Password needs to be at least 8 characters long.", 400)

    else:
        return('', 204)


def check_auth(u, t):
    creds = db.get_user_creds(u)
    if creds == t:
        return True
    else:
        return False


@app.route('/files', methods=['GET', 'POST', 'DELETE'])
def files():
    user = request.headers.get('UserId')
    token = request.headers.get('X-Session')
    auth = check_auth(user, token)
    if not auth:
        return ('Forbidden', 403)

    if request.method == 'POST':
        name, content = request.data.split(b'=', 1)
        try:
            db.put_user_file(user, name, content)
        except Exception:
            return ('', 500)
        else:
            return ('', 204)

    elif request.method == 'GET':
        if not request.args:
            files = db.user_files.items()
            new_dict = dict(files)
            filenames = []
            for k in new_dict[user]:
                try:
                    filenames.append(list(k)[0].decode('utf-8'))
                except Exception as e:
                    print(e)

            j = {'files': filenames}
            data = json.dumps(j)
            response = app.make_response((data, 200))
            response.headers['Content-Type'] = 'application/json'
            return response
        filename = request.args.get("filename")
        try:
            content = db.get_user_file(user, str.encode(filename))
            if content is None:
                return ('Not Found', 404)
        except Exception as e:
            return ('', 500)
        else:
            response = app.make_response((content, 200))
            response.headers['Content-Length'] = str(len(content))
            response.headers['Content-Type'] = 'application/octet-stream'
            return response

    elif request.method == 'DELETE':
        if not request.is_json:
            return ('', 400)

        filename = request.json.get('filename', None)
        filename = str.encode(filename)
        try:
             db.delete_user_file(user, filename)
        except Exception:
            return ('', 500)
        else:
            return ('', 204)


@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return ('', 400)

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    try:
        assert USERS[username] == password
    except Exception:
        return ('Username nor password not correct', 400)
    else:
        token = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(32)])
        db.put_user_credentials(username, token)
        response = app.make_response(('Success', 200))
        response.headers['X-Session'] = token
        response.headers['UserId'] = username
        return response


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

