import asyncpg
from environs import Env
from config import logger
from typing import List, Dict, Tuple
import asyncio


class Database:
    def __init__(self):
        self.env = Env()
        self.env.read_env(path='config/.env')

        self.user = self.env.str('DB_USER')
        self.password = self.env.str('DB_PASSWORD')
        self.host = self.env.str('DB_HOST')
        self.db_name = self.env.str('DB_NAME')
        self.db_port = self.env.str('DB_PORT')
        self.pool = None

    async def create_pool(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=self.user,
                password=self.password,
                host=self.host,
                database=self.db_name,
                port=self.db_port,
            )

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while creating connection pool", error)
            print(error)

    async def close_pool(self):
        if self.pool:
            await self.pool.close()

    async def execute_query(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while executing query", error)

    async def execute_query_return(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetch(query, *args)
                return result
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while executing query", error)
            return []

    async def fetch_row(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while fetching row", error)

    async def fetch_all(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while fetching all", error)

    async def db_start(self) -> None:
        """
        Initializes the connection to the database and creates the tables if they do not exist.
        """
        try:
            await self.create_pool()

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    subscription BOOLEAN DEFAULT FALSE,
                    sub_start_date TEXT DEFAULT 'No',
                    sub_end_date TEXT DEFAULT 'No',
                    balance INT DEFAULT 0,
                    partner_program TEXT DEFAULT 'No',
                    mon_keywords TEXT DEFAULT 'No',
                    mon_status BOOLEAN DEFAULT FALSE
                )
            """)
            logger.info('connected to database')

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while connecting to DB", error)

    async def add_user(self, username: str, user_id: int):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users (user_id, username)
                    SELECT $1, $2
                    WHERE NOT EXISTS (
                        SELECT 1 FROM users WHERE user_id = $1
                    )
                """, user_id, username)

                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS monitor_list_{user_id} (
                        chat_name TEXT,
                        chat_id BIGINT PRIMARY KEY,
                        chat_type TEXT DEFAULT 'Standart'
                    )
                """.format(user_id=user_id))

        except Exception as error:
            print("Error while adding user:", error)

    async def get_user_info(self, user_id: int) -> str:
        try:
            async with self.pool.acquire() as conn:
                # Подготовим SQL-запрос для получения информации о пользователе
                query = """
                    SELECT * FROM users WHERE user_id = $1
                """

                # Выполним запрос и получим результат
                result = await conn.fetchrow(query, user_id)

                # Если результат не пустой, преобразуем его в строку
                if result:
                    user_info = f"🔹<b>ID:</b> {result['user_id']}\n"
                    user_info += f"🔹<b>Username:</b> {result['username']}\n"
                    user_info += f"🔹<b>Баланс:</b> {result['balance']}\n"
                    user_info += f"🔹<b>Подписка:</b> {'Активирована' if result['subscription'] else 'Не активирована'}\n"
                    user_info += f"🔹<b>Дата начала подписки:</b> {result['sub_start_date'] if not 'No' else 'Нет'}\n"
                    user_info += f"🔹<b>Дата окончания подписки:</b> {result['sub_end_date'] if not 'No' else 'Нет'}\n"
                    user_info += f"🔹Приглашенные пользователи: {result['partner_program'] if not 'No' else 'Нет'}\n"
                    user_info += f"🔹Реферальная ссылка: www.google.com \n"
                    return user_info
                else:
                    return "User not found."

        except Exception as error:
            print("Error while getting user info:", error)
            return "Error while getting user info."

    # chat settings
    async def get_monitor_list(self, user_id: int) -> List[Dict]:
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT * FROM monitor_list_{user_id}
                """.format(user_id=user_id)

                result = await conn.fetch(query)

                monitor_list = [dict(record) for record in result]
                return monitor_list

        except Exception as error:
            print("Error while getting monitor list:", error)
            return []

    async def add_to_monitor_list(self, user_id: int, chat_name: str, chat_id: int, chat_type: str = 'Standard') -> None:
        try:
            async with self.pool.acquire() as conn:
                query = """
                    INSERT INTO monitor_list_{user_id} (chat_name, chat_id, chat_type)
                    VALUES ($1, $2, $3)
                """.format(user_id=user_id)

                await conn.execute(query, chat_name, chat_id, chat_type)

        except Exception as error:
            print("Error while adding to monitor list:", error)

    async def remove_from_monitor_list(self, user_id: int, chat_id: int) -> None:
        try:
            async with self.pool.acquire() as conn:
                query = """
                    DELETE FROM monitor_list_{user_id}
                    WHERE chat_id = $1
                """.format(user_id=user_id)

                await conn.execute(query, chat_id)

        except Exception as error:
            print("Error while removing from monitor list:", error)

#  keywords settings
    async def add_keywords(self, user_id: int, keywords: List[str]) -> None:
        try:
            async with self.pool.acquire() as conn:
                # Подготовим SQL-запрос для добавления ключевых слов в столбец mon_keywords
                query = """
                    UPDATE users
                    SET mon_keywords = mon_keywords || $1
                    WHERE user_id = $2
                """

                # Преобразуем список ключевых слов в формат массива PostgreSQL
                keywords_array = list(map(str, keywords))

                # Выполним запрос с указанными параметрами
                await conn.execute(query, keywords_array, user_id)

        except Exception as error:
            print("Error while adding keywords:", error)

    async def remove_keywords(self, user_id: int, keyword: str) -> None:
        try:
            async with self.pool.acquire() as conn:
                # Подготовим SQL-запрос для удаления ключевого слова из столбца mon_keywords
                query = """
                    UPDATE users
                    SET mon_keywords = array_remove(mon_keywords, $1)
                    WHERE user_id = $2
                """

                # Выполним запрос с указанными параметрами
                await conn.execute(query, keyword, user_id)

        except Exception as error:
            print("Error while removing keyword:", error)

    async def get_all_keywords(self, user_id: int) -> List[str]:
        try:
            async with self.pool.acquire() as conn:
                # Подготовим SQL-запрос для получения всех ключевых слов из столбца mon_keywords
                query = """
                    SELECT mon_keywords
                    FROM users
                    WHERE user_id = $1
                """

                # Выполним запрос и получим результат
                result = await conn.fetchval(query, user_id)

                # Если результат не пустой, преобразуем его в список ключевых слов
                if result:
                    return result
                else:
                    return []

        except Exception as error:
            print("Error while getting keywords:", error)
            return []


db = Database()