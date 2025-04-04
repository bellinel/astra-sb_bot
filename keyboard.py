from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton 
from aiogram.utils.keyboard import InlineKeyboardBuilder,ReplyKeyboardBuilder
from text_messages import TextButtons

async def get_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(text=TextButtons.WORK_IN, request_location=True),
        
    )
    return keyboard.as_markup(resize_keyboard=True)


async def get_work_left_keyboard() -> InlineKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(text=TextButtons.LEFT_WORK, request_location=True),
        KeyboardButton(text=TextButtons.CHANGE_WORK)
        
    )
    return keyboard.as_markup(resize_keyboard=True)

async def get_change_work_keyboard() -> InlineKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(text=TextButtons.NEW_WORK, request_location=True),
    )
    return keyboard.as_markup(resize_keyboard=True)

async def get_new_day_keyboard() -> InlineKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(text=TextButtons.NEW_DAY)
    )
    return keyboard.as_markup(resize_keyboard=True)

async def get_report_keyboard() -> InlineKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(text='Да'),
        KeyboardButton(text='Нет')
    )
    return keyboard.as_markup(resize_keyboard=True)

