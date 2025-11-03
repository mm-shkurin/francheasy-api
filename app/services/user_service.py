from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.users import Users
from datetime import datetime
from loguru import logger

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_or_get_vk_user(self, vk_id: str, vk_json: str):
        logger.info(f"Looking for user with vk_id: {vk_id}")
        logger.debug("vk_json received")
        exists = await self.db.execute(select(Users).where(Users.vk_id == vk_id))
        user = exists.scalar_one_or_none()

        logger.debug(f"Looking for user with vk_id again: {vk_id}")
        if not user:
            logger.info("Creating new user (vk)")
            new_user = Users(vk_id=vk_id, vk_json=vk_json)
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            logger.info(f"New user created with id: {new_user.id}")
            return new_user.id
        else:
            logger.info(f"Updating existing user: {user.id}")
            user.vk_json = vk_json
            await self.db.commit()
            logger.debug("User vk_json updated")
            return user.id