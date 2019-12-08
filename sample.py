from src.dion import execute_query
from src.session import Session
from src.models import Classification


s = Session('username', Classification.TS, Classification.S, Classification.C)
result = execute_query(s, "select * from patients where national_code = '123'")
print(result)
