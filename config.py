from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted

from model import *
from datetime import datetime

TOKEN = '5326957770:AAHFXPFO5eDQgi1z5ylOI3We_tAczKg4U3Q'


session = Session()


bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())