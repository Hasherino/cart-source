import psycopg2 as pg

def get_connection():
    try:
        return pg.connect(
            host="db",
            port=5432,
            user="postgres",
            password="postgres"
        )
    except Exception as e:
        raise Exception("Database connection error: ", e) 
    
def get_map():
    try:
        with get_connection() as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM objects;")
                return curs.fetchall()
    except (Exception, pg.DatabaseError) as error:
        print("Exception occured while retrieving products: ", error)
        return None
