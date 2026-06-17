from pydantic import BaseModel, ConfigDict, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description='Email do usuario')
    senha: str = Field(..., description='Senha do usuario', min_length=6)

class LoginResponseData(BaseModel):
    access_token: str = Field(..., description='Token JWT para autenticacao')
    token_type: str = Field('bearer', description='Tipo do token')
    nome: str = Field(..., description='Nome do usuario autenticado')
    email: str = Field(..., description='Email do usuario autenticado')

    model_config = ConfigDict(from_attributes=True)
