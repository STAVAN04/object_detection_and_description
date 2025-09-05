from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

pwd_crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth = OAuth2PasswordBearer(tokenUrl="auth/login")

ALGORITHM = "HS256"
SECRET_KEY = "08b1b1e80aca837e12ff52a9197a321c9d41d48f4c6b415367df1140d7d5cb0c"
REFRESH_SECRET_KEY = "f1ce1380fc4a6be85046143db4eca66076c3f7a2e297b0e1d6c1ad599a48320b"
ACCESS_EXPIRY = 30
REFRESH_EXPIRY = 30
