from fact.libraries.jwt import JWT

class LoginSerializer:
    def __init__(self, user):
        self.role = user.role.name
        self.token = JWT().encode({
            "id": user.id,
            "name": user.name,
            "email": user.email
        })

    def json(self):
        return {
            "role": self.role,
            "token": self.token
        }
