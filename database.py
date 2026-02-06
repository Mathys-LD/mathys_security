import pymysql

def get_connection():
    try:
        connection = pymysql.connect(
            host="mysql-tutel.alwaysdata.net",
            user="tutel",
            password="Sdkfz234/",
            database="tutel_securite",
            charset="utf8mb3",
            port=3306,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print("Erreur MySQL :", e)
        return None