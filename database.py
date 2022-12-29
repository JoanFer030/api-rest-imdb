import psycopg2
from decouple import config

class DB:
    def __init__(self):
        self.aux_connect()

    def aux_connect(self):
        self.conn = psycopg2.connect(
        host=config("DB_HOST"),
        database=config("DB_NAME"),
        user=config("DB_USER"),
        password=config("DB_PSW")
        )
        self.cursor = self.conn.cursor()

    def connect(self):
        status = self.conn.closed
        if status:
            self.aux_connect()
            try:
                self.cursor.execute("SELECT version()")
            except:
                self.connect()
        else:
            try:
                self.cursor.execute("SELECT version()")
            except:
                self.connect()

    def select(self, query):
        self.connect()
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def insert(self, table, values):
        self.connect()
        set_values = ""
        for val in values:
            if type(val) == str:
                set_values += f"'{val}', "
            else:
                set_values += f"{val}, "
        set_values = set_values[:-2]
        query = f"""
            INSERT INTO {table}
            VALUES({set_values})
        """
        self.cursor.execute(query)
        self.conn.commit()

    def update(self,table, values, cod):
        self.connect()
        set_values = ""
        for col, val in values.items():
            if type(val) == str:
                set_values += f"{col}='{val}', "
            else:
                set_values += f"{col}={val}, "
        set_values = set_values[:-2]
        query = f"""
            UPDATE {table}
            SET {set_values}
            WHERE codigo='{cod}'
        """
        self.cursor.execute(query)
        self.conn.commit()

    def delete(self, table, cod, where="codigo"):
        self.connect()
        query = f"""
            DELETE FROM {table}
            WHERE {where}='{cod}'
        """
        self.cursor.execute(query)
        self.conn.commit()

    def close(self):
        self.conn.close()

# Ejemplo
if __name__ == "__main__":
    db = DB()
    print(db.select("SELECT * FROM teams"))