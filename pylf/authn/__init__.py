

class Authenticator:
    @classmethod
    def from_config(cls, cfg):
        return cls()

    def authenticate(self, login, password):
        raise NotImplementedError
