import asyncio
import logging
import random

from config import BOT_TOKEN, CHAT_ID, OWNER_ID, CONDITIONS, EXTRA_IDS
import sqlite3

import aiosqlite
from aiogram import Router, Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    ChatMember,
    CallbackQuery,
    FSInputFile,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.formatting import Text, Bold
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties


async def main():
    router = Router()

    @router.message(CommandStart())
    async def start_command(message: Message):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="Кнопка", callback_data="button"))
        if message.from_user.id == OWNER_ID:
            builder.add(
                InlineKeyboardButton(
                    text="Вывести список пользователей", callback_data="show_list"
                )
            )
            builder.add(
                InlineKeyboardButton(
                    text="Начать жеребьёвку", callback_data="start_lottery"
                )
            )
        await message.answer(
            text="Вас приветсвует служба поддержки Деда Мороза!\n"
            "К сожалению, я сейчас очень занят и не могу подарить\n"
            "подарки всем хорошим мальчикам и девочкам :-(\n"
            "Но вы можете помочь мне в этой непростой задаче, нажав на Кнопку!",
            reply_markup=builder.as_markup(),
        )
        if CONDITIONS:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Ознакомьтесь с условиями: \n" + CONDITIONS,
            )

    @router.callback_query(F.data == "button")
    async def button_callback(callback: CallbackQuery):
        member = await bot.get_chat_member(
            chat_id=CHAT_ID, user_id=callback.from_user.id
        )
        if not (
            isinstance(member, ChatMember) or (callback.from_user.id not in EXTRA_IDS)
        ):
            await callback.answer(text="Похоже вы за пределами узкого круга...")
            return
        try:
            async with aiosqlite.connect("./db/database.db") as db:
                await db.execute(
                    "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)"
                )
                await db.execute(
                    "INSERT INTO users (user_id, username) VALUES (?,?)",
                    ([callback.from_user.id, callback.from_user.username]),
                )
                await db.commit()
        except sqlite3.IntegrityError:
            print(f"Пользователь {callback.from_user.username} уже зарегистрирован")
            await bot.send_message(callback.from_user.id, "Вы уже зарегистрированы!")
            return
        else:
            await callback.message.answer(
                "Вы великолепны! Ожидайте жеребьёвки! 🎉", show_alert=True
            )

    @router.callback_query(F.data == "show_list")
    async def show_list_callback(callback: CallbackQuery):
        async with aiosqlite.connect("./db/database.db") as db:
            users = []
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users") as cursor:
                async for row in cursor:
                    users.append(row["username"])
            await bot.send_message(callback.from_user.id, "\n".join(users))

    @router.callback_query(F.data == "start_lottery")
    async def start_lottery_callback(callback: CallbackQuery):
        await bot.send_message(callback.from_user.id, "Жеребьёвка началась!")
        async with aiosqlite.connect("./db/database.db") as db:
            users = {}
            pairs = {}
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users") as cursor:
                async for row in cursor:
                    users.update({row["user_id"]: row["username"]})
            for user_id in users:
                rest_users = [
                    i for i in users if ((i != user_id) and (i not in pairs.values()))
                ]
                pairs.update({user_id: random.choice(rest_users)})
        await bot.send_message(
            callback.from_user.id,
            "\n".join(
                [f"{users[user_id]}: {users[pairs[user_id]]}" for user_id in users]
            ),
        )
        ded_pic = FSInputFile("./img/ded.gif")
        for user_id in users:
            msg = Text(
                Bold("Жеребьёвка закончена!\n"),
                f"Поздравьте -> @{users[pairs[user_id]]} <- ",
            )
            await bot.send_photo(chat_id=user_id, photo=ded_pic)
            await bot.send_message(chat_id=user_id, **msg.as_kwargs())

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
