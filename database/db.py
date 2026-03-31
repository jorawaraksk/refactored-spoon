import motor.motor_asyncio
from config import DB_URI, DB_NAME

class Database:
    def __init__(self, uri, database_name):
        # Initialize the async MongoDB client
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            session=None,
        )

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)

    async def add_user(self, id, name):
        if not await self.is_user_exist(id):
            user = self.new_user(id, name)
            await self.col.insert_one(user)

    async def get_all_users(self):
        # Returns an async cursor for the broadcast loop
        return self.col.find({})

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session', None) if user else None

# Instantiate the database object so it can be imported by other files
db = Database(DB_URI, DB_NAME)
