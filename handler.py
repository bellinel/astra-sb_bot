from datetime import datetime
from sre_parse import State
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os

from dotenv import load_dotenv
from geocoder import GeocodingService
from orm import add_user_to_db, get_all_workers, delete_all_workers
from create_google_table import write_to_sheet
from text_messages import TextMessages
from text_messages import TextButtons
from keyboard import get_start_keyboard, get_work_left_keyboard, get_change_work_keyboard, get_new_day_keyboard, get_report_keyboard
workers_router = Router()

# Загружаем переменные окружения
load_dotenv()

# Получаем ID группового чата
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # Значение по умолчанию как fallback


class Worker(StatesGroup):
    work_in = State()
    left_work = State()
    change_work = State()
    new_work = State()

@workers_router.message(Command("start"))
@workers_router.message(F.text == TextButtons.NEW_DAY)

async def cmd_start(message: Message, state: FSMContext):
    
    
        await message.answer(TextMessages.START, reply_markup=await get_start_keyboard())
        await state.set_state(Worker.work_in)

@workers_router.message(Worker.work_in)
async def work_in(message: Message, state: FSMContext, bot: Bot):
    
    if message.text == '/report':
        await state.clear()
        await report(message, state)
    if message.location:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        latitude = message.location.latitude
        longitude = message.location.longitude
        geocoder = GeocodingService()
        start_address = await geocoder.get_address_by_coordinates(latitude, longitude)
        start_address = start_address.get("full_address")
        
        time_to_start_work = datetime.now()
        
            
            
        
        # Форматируем время для пользователя
        formatted_time = time_to_start_work.strftime("%d.%m.%Y %H:%M:%S")
        
        await state.update_data(user_id=user_id, user_name=user_name, start_address=start_address, time_to_start_work=time_to_start_work)
        await message.answer(f"Вы пришли на объект по адресу: \n<i>{start_address}</i>\nВремя прибытия: <i>{formatted_time}</i>", reply_markup=await get_work_left_keyboard(), parse_mode="HTML")
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=TextMessages.START_WORK_FOR_MENAGES.format(user_name=user_name, start_address=start_address, time_to_start_work=formatted_time))
        await state.set_state(Worker.left_work)
        


@workers_router.message(Worker.left_work)
async def left_work(message: Message, state: FSMContext, bot: Bot):
    
    if message.text == TextButtons.CHANGE_WORK:

        data = await state.get_data()
        left_address = data.get("start_address")
        time_to_left_work = datetime.now()
        formatted_time = time_to_left_work.strftime("%d.%m.%Y %H:%M:%S")
        
        
        
        await message.answer(f"Вы закончили работу на объекте по адресу: \n<i>{left_address}</i>\nВремя ухода: <i>{formatted_time}</i>", reply_markup=await get_change_work_keyboard(), parse_mode="HTML")
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=TextMessages.CHANGE_WORK_FOR_MENAGES.format(user_name=message.from_user.first_name, left_address=left_address, time_to_left_work=formatted_time))
        data.update(left_address=left_address, time_to_left_work=time_to_left_work)
        
        work_time = 'Переход на новый объект'
        data.update(work_time=work_time)
        
        
        await state.set_state(Worker.change_work)



    elif message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
        geocoder = GeocodingService()
        left_address = await geocoder.get_address_by_coordinates(latitude, longitude)
        left_address = left_address.get("full_address")
        time_to_left_work = datetime.now()
        
        # Форматируем время для пользователя
        formatted_time = time_to_left_work.strftime("%d.%m.%Y %H:%M:%S")

        await state.update_data(left_address=left_address, time_to_left_work=time_to_left_work)
        data = await state.get_data()
        
        time_to_start_work = data.get("time_to_start_work")
        work_time = time_to_left_work - time_to_start_work
        
        if data.get("start_work_time"):
            work_time = time_to_left_work - data.get("start_work_time")
            data.pop("start_work_time")
            data.update(work_time=work_time)
            
            print('В чендж ворке')
    
        hours, remainder = divmod(work_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        work_time_str = f"{int(hours)} часов {int(minutes)} минут {int(seconds)} секунд"
        
        
        data.update(work_time = work_time_str)
        await add_user_to_db(data)
        await message.answer(f"Вы закончили на работу по адресу: \n<i>{left_address}</i>\nВремя ухода: <i>{formatted_time}</i>", parse_mode="HTML")
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=TextMessages.LEFT_WORK_FOR_MENAGES.format(user_name=message.from_user.first_name, left_address=left_address, time_to_left_work=formatted_time, work_time=work_time_str), parse_mode="HTML")
        await message.answer(TextMessages.WORK_TIME.format(work_time=work_time_str))
        await message.answer(TextMessages.LEFT_WORK, reply_markup=await get_new_day_keyboard())
        await state.clear()







@workers_router.message(Worker.change_work)
async def change_work(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        latitude = message.location.latitude
        longitude = message.location.longitude
        geocoder = GeocodingService()
        start_address = await geocoder.get_address_by_coordinates(latitude, longitude)
        start_address = start_address.get("full_address")
        time_to_start_work = datetime.now()
        if data.get("start_work_time"):
            start_work_time = data.get("start_work_time")
            work_time = "Переход на новый объект"
        else:
            start_work_time = data.get("time_to_start_work")
            work_time = "Переход на новый объект"
            
            
        
        # Форматируем время для пользователя
        formatted_time = time_to_start_work.strftime("%d.%m.%Y %H:%M:%S")
        
        await state.update_data(user_id=user_id, user_name=user_name, start_address=start_address, time_to_start_work=time_to_start_work, start_work_time=start_work_time, work_time=work_time)
        await message.answer(f"Вы пришли на объект по адресу: \n<i>{start_address}</i>\nВремя прибытия: <i>{formatted_time}</i>", reply_markup=await get_work_left_keyboard(), parse_mode="HTML")
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=TextMessages.NEW_WORK_FOR_MENAGES.format(user_name=message.from_user.first_name, new_address=start_address, time_to_new_work=formatted_time))
        await state.set_state(Worker.left_work)
        
    
    


@workers_router.message(Command("report"))
async def report(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(TextMessages.REPORT, reply_markup=await get_report_keyboard())
         
@workers_router.message(F.text == 'Да')
async def report_yes(message: Message, state: FSMContext):
    workers = await get_all_workers()
    url = await write_to_sheet(workers)
    
    await message.answer(url.get("url"))
    await state.clear()
    await delete_all_workers()
    await cmd_start(message, state)

@workers_router.message(F.text == 'Нет')
async def report_no(message: Message, state: FSMContext):
    await state.clear()
    await cmd_start(message, state)
    return



