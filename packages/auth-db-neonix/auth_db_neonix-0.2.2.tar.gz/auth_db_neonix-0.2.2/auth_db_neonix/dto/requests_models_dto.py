from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str
    model_config = {
        "arbitrary_types_allowed": True,
        "strict": False
    }


class RegisterRequest(BaseModel):
    email: str
    password: str
    fernet_client_key: str
    model_config = {
        "arbitrary_types_allowed": True,
        "strict": False
    }


class UserRequest(BaseModel):
    username: str
    email: str
    userId: str
    jwt: str
    settings: [str]
    model_config = {
        "arbitrary_types_allowed": True,
        "strict": False
    }


class SettingsRequest(BaseModel):
    type: str
    is_default: bool
    id: int
    name: str
    wt: str
    settings: str
    model_config = {
        "arbitrary_types_allowed": True,
        "strict": False
    }

