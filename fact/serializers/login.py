from fact.libraries.jwt import JWT

class LoginSerializer:
    def __init__(self, user):
        self.token = JWT().encode({
            "id": user.id,
            "name": user.name,
            "email": user.email
        })

    def json(self):
        return {
            "token": self.token
        }
