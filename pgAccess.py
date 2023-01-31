import psycopg2
import os
from dotenv import load_dotenv


class myConnection:
    def __init__(self) -> None:
        load_dotenv()

        self.connection = psycopg2.connect(database='credParameters',
                                    host='172.18.0.2',
                                    user=os.getenv('PG_USERNAME'),
                                    password=os.getenv('PG_PASSWORD'),
                                    port='5432')
        self.cursor = self.connection.cursor()

    def __del__(self) -> None:
        self.cursor.close()
        self.connection.close()

    def insertUser(self, values: dict) -> None:
        try:
            self.cursor.execute(f"INSERT INTO person (id, user_name, phone) \
                    VALUES({values['id']}, '{values['user_name']}', '{values['phone']}')")
        except Exception as e:
            print(e)
        self.connection.commit()

    def insertAd(self, values:dict) -> None:
        try:
            self.cursor.execute(f"INSERT INTO advertisement (id, add_date, \
                                    owners_num, last_operation, operation_description, \
                                    ad_link, user_id) \
                                VALUES({values['id']}, {values['add_date']}, {values['owners_num']} \
                                    {values['last_operation']}, {values['operation_description']}, {values['ad_link']}, {values['user_id']})")
            self.connection.commit()
        except Exception as e:
            print(e)