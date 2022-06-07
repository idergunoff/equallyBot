from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from model import *

TOKEN = '5258477706:AAHoPOnor-yQQ1eaMIeSOsmvzTEu7hwgCss' # заменить



session = Session()


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())