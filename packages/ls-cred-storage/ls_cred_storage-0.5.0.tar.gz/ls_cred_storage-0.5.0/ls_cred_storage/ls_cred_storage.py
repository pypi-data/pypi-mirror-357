
import keyring
import time
import json
import os


class LSCredStorage():
    USER_KEY = 'userToken'
    TIMESTAMP_KEY = 'timestamp'
    USER_ID_KEY = 'userId'
    SESSION_TOKEN_KEY = 'sessionToken'
    ACCESS_TOKEN_KEY = 'accessToken'
    MAX_TOKEN_RETENTION_TIME_SECS = 3500
    APP_SERVICE_NAME = 'LightSolverClient'


    def __init__(self,token = None):
        self.currentTokenDic = token

    def is_cached_user(self, userName):
        return self.currentTokenDic[self.USER_KEY] == userName

    def update_current_token(self,token):
        self.currentTokenDic = token

    def store_token(self, username, token):
        self.update_current_token(token)
        if os.name == "nt":
            keyring.set_password(self.APP_SERVICE_NAME, username, token)
        else:
            with open("tokens.data", "w") as f:
                f.write(json.dumps(token))

    def remove_token(self, username):
        if os.name == "nt":
            keyring.delete_password(self.APP_SERVICE_NAME, username)
        else:
            raise Exception("Removing cached tokens is not supported for this OS.")

    def get_stored_token(self, username):
        if os.name == "nt":
            data= keyring.get_password(self.APP_SERVICE_NAME, username)
            if data != None:
                token =  json.loads(data.replace("'", "\""))
                self.update_current_token(token)
                return token
            return None
        else:
            filename = f"tokens.data"
            if not os.path.isfile(filename):
                return None
            with open(filename, "r") as f:
                data = f.readline()
                token =  json.loads(data.replace("'", "\""))
                if token[self.USER_KEY] == username:
                    self.update_current_token(token)
                    return token
                else:
                    return None
                    

    def is_token_valid(self):
        if self.currentTokenDic != None:
          return time.time() - self.currentTokenDic[self.TIMESTAMP_KEY] < self.MAX_TOKEN_RETENTION_TIME_SECS
        return False
