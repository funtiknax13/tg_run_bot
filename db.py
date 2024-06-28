import sqlite3

import psycopg2


class DBmanager:

    def __init__(self, db_name: str, params: dict):
        self.db_name = db_name
        self.params = params

    async def create_table(self):
        """
        Создание таблицы
        """

        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sneakers (
                sneakers_id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                brand VARCHAR(30) NOT NULL,
                model VARCHAR(100),
                photo TEXT,
                distance REAL DEFAULT 0,
                create_date TIMESTAMP,
                description TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS run (
                run_id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                track TEXT NOT NULL,
                run_date DATE NOT NULL,
                distance REAL NOT NULL,
                run_time TIME NOT NULL,
                create_date TIMESTAMP,
                description TEXT,
                sneakers INTEGER,
                is_moderate BOOLEAN DEFAULT False,
                FOREIGN KEY (sneakers) REFERENCES sneakers (sneakers_id) ON DELETE SET NULL
            )
        """)

        conn.commit()
        cur.close()
        conn.close()

    async def add_run(self, **kwargs):
        """
        Добавление пробежки
        :return: None
        """
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        cur = conn.cursor()
        cur.execute("""INSERT INTO run (user_id, track, run_date, distance, run_time, create_date, description,
         sneakers, is_moderate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING run_id""",
                    (kwargs["user_id"], kwargs["track"], kwargs["run_date"], kwargs["distance"], kwargs["run_time"],
                     kwargs["create_date"], kwargs["description"], kwargs["sneakers"], kwargs["is_moderate"]))
        conn.commit()
        cur.close()
        conn.close()

    async def get_run_list(self, user_id: int):
        """
        Вывод списка задач пользователя
        :param user_id: tg id пользователя
        :return:
        """
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        cur = conn.cursor()
        cur.execute(f"""SELECT * FROM run
                    WHERE user_id = {user_id} ORDER BY run_date""")
        data = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return data

    async def add_sneakers(self, **kwargs):
        """
        Добавление кроссовок
        :return: None
        """
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        cur = conn.cursor()
        cur.execute("""INSERT INTO sneakers (user_id, brand, model, photo, distance, create_date, description)
         VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING sneakers_id""",
                    (kwargs["user_id"], kwargs["brand"], kwargs["model"], kwargs["photo"], kwargs["distance"],
                     kwargs["create_date"], kwargs["description"]))
        conn.commit()
        cur.close()
        conn.close()

    async def get_sneakers_list(self, user_id: int):
        """
        Вывод списка кроссовок пользователя
        :param user_id: tg id пользователя
        :return:
        """
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        cur = conn.cursor()
        # cur.execute(f"""SELECT * FROM sneakers
        #             WHERE user_id = {user_id}""")
        cur.execute(f"""SELECT sneakers_id, user_id, brand, model, photo, distance, create_date, description,
                    ((SELECT SUM(run.distance) FROM run
                    WHERE run.sneakers = sneakers.sneakers_id) + distance)
                    AS new_distance
                    FROM sneakers
                    WHERE user_id =  {user_id}""")
        data = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return data

    async def get_sneakers(self, sneakers_id: int):
        """
        Вывод пары кроссовок по id
        :param sneakers_id: id кроссовок пользователя
        :return:
        """
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        cur = conn.cursor()
        cur.execute(f"""SELECT * FROM sneakers
                    WHERE sneakers_id = {sneakers_id}""")
        data = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return data


