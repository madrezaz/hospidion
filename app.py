from src.session import Session
from src.models import Classification
from src.dion import execute_query
import config
import psycopg2

def databaseConnection():
    try:
        connection = psycopg2.connect(dbname=config.db_name, user=config.db_user, password=config.db_password,host=config.db_host, port=config.db_port)
        cursor = connection.cursor()
        return cursor,connection 
    except (Exception, psycopg2.Error) as error :
        print ("Error in database connection!", error)
        if(connection):
            cursor.close()
            connection.close()
            return None
    
def authenticate():       
    print("***Welcome to secure hospital***")
    cur,con = databaseConnection()
    query = None
    if cur:
        pid = None
        type = None
        section = None
        mange_role = None
        role = None
        for i in range(3):
            username = input("username:")
            password = input("password:")
            record = None
            query = "select * from users where username = '%s' and password = '%s'" % (username, password)
            cur.execute(query)
            record = cur.fetchone()
            if record:
                type = record[2]
                break
            else:
                print("Your password or username is not correct!")
            if i == 2:
                print("You try it three times come later!")
                return None
        if type == 'physicians':
            query = "select s_asl,s_rsl,s_wsl,personnel_id,section,management_role from %s where username = '%s'" % (type,username)
        elif  type == 'nurses':
            query = "select s_asl,s_rsl,s_wsl,personnel_id,section from %s where username = '%s'" % (type,username)
        elif type == 'patients':
            query = "select s_asl,s_rsl,s_wsl,section from %s where username = '%s'" % (type,username)
        else:
            query = "select s_asl,s_rsl,s_wsl,role from %s where username = '%s'" % (type,username)
        cur.execute(query)
        record = cur.fetchone()
        asl = record[0]
        rsl = record[1]
        wsl = record[2]
        if len(record) == 6:
            pid = record[3]
            section = record[4]
            mange_role = record[5]
        if len(record) == 5:
            pid = record[3]
            section = record[4]
        elif len(record) == 4:
            if type == 'patients':
                section = record[3]
            else:
                role = record[3]
        s = Session(type, pid, section, username, mange_role, role, Classification(asl), Classification(rsl), Classification(wsl))
        return s,cur,con
    else:
        print("Sorry something is wrong come later!")
        return None
    
s,cur,con = authenticate()
if s:
    print("+++Hello ",s.type,"+++")
    query = input("Enter your query:")
    while(query is not 'q'):
        result = execute_query(s,cur, con, query)
        if result == 'None':
            print("There are not any records")
        else:
            print(result)
        query = input("Enter your query:")
        
