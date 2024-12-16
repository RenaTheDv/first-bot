import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage   #хранить состояние в памяти
from aiogram.fsm.state import StatesGroup, State       #какое сейчас состояние?
from aiogram.fsm.context import FSMContext             #управление состоянием

from config import TOKEN, TRANSLATE_TABLE, HELP_COMMANDS, CORRECT_SYMBOLS            #правь файл (добавь свой ТОКЕН)


bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

class Transl(StatesGroup):
    translating = State()

def translating_to_latin(text):
    table_to_translate = TRANSLATE_TABLE
    translated = ''
    for s in text.lower():
        if s in table_to_translate:
            translated += table_to_translate[s]
        else:
            translated += s
    return translated

def valid_name(text):
    return all(s in CORRECT_SYMBOLS or s.isspace() for s in text.lower())


@dp.message(Command(commands=['start']))
async def command_start(message:types.Message):
    user_name = message.from_user.full_name
    user_id = message.from_user.id
    text = f'Привет, {user_name}! Этот бот был создан для обучения. Напиши команду /help для изучения команд.'
    logging.info(f'{user_id}.{user_name} запустил бота.')
    await bot.send_message(chat_id=user_id, text=text)


@dp.message(Command(commands=['help']))
async def command_help(message:types.Message):
    logging.info('Была запрошена команда HELP.')
    await bot.send_message(chat_id=message.chat.id,
                           text=HELP_COMMANDS,
                           parse_mode='HTML')


@dp.message(Command(commands=['start_translate']))
async def command_start_translate(message:types.Message, state=FSMContext):
    logging.info('Включен режим перевода.')
    await message.answer('Режим перевода на латиницу включен. Введите ФИО.')
    await state.set_state(Transl.translating)


@dp.message(Command(commands=['stop_translate']))
async def command_stop_translate(message:types.Message, state=FSMContext):
    logging.info('Выключен режим перевода.')
    await message.answer('Режим перевода ФИО на латиницу отключен.')
    await state.clear()


@dp.message(Transl.translating)         #команда в режиме перевода
async def translate_message(message:types.Message, state:FSMContext):
    logging.info('Вызов перевода в режиме перевода.')
    text = message.text
    words = text.split()
    if len(words) == 2 or len(words) == 3:
        if valid_name(text):
            translated_text = translating_to_latin(text)
            await message.answer(translated_text.title())
        else:
            await message.answer('Вы вводите неверный формат ФИО. Ожидаю верный формат...')
    else:
        await message.answer('Введите ФИО в формате "Фамилия Имя Отчество".')


@dp.message()
async def echo(message:types.Message):
    user_name = message.from_user.full_name
    user_id = message.from_user.id
    logging.info(f'{user_id}.{user_name}: {message.text}')
    await message.answer(message.text)


if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=True)
    