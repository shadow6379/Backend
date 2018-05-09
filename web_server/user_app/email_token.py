from itsdangerous import URLSafeTimedSerializer as utsr
from web_server.settings import SECRET_KEY
import base64


# Token class, using for creating token
class Token:
    # initialize the class
    # using base64 to  encrypt the security_key
    def __init__(self, security_key):
        self.security_key = security_key
        self.salt = base64.encodebytes(security_key.encode('utf-8')).decode('utf-8')

    # serializing the itsdangerous, which contains the timestamp
    def generate_validate_token(self, username):
        serializer = utsr(self.security_key)
        # convert the serializer to the json form
        return serializer.dumps(username, self.salt)

    # validating the token
    # the period of validity is expiration second(s), default = 3600s
    # return the username if it is in period
    def confirm_validate_token(self, token, expiration=3600):
        serializer = utsr(self.security_key)
        return serializer.loads(
            token,
            salt=self.salt,
            max_age=expiration
        )

    # whether it is in period, it returns a username
    def remove_validate_token(self, token):
        serializer = utsr(self.security_key)
        return serializer.loads(token, salt=self.salt)


# define it the global variable
token_confirm = Token(SECRET_KEY)
