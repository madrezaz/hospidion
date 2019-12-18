import psycopg2
import config


def do_the_login(username, password):
    connection = psycopg2.connect(dbname=config.db_name, user=config.db_user, password=config.db_password,
                                  host=config.db_host, port=config.db_port)
    cursor = connection.cursor()
    cursor.execute("select * from users where username = %s and password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user is not None
