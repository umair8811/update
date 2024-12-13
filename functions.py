from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_Password_check(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password) 

def hashing_pass(password :str):
    return pwd_context.hash(password)