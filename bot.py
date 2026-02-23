import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Загружаем переменные окружения
load_dotenv()
API_TOKEN = os.getenv("TG_BOT_TOKEN")
ALLOWED_CHAT_ID = int(os.getenv("ALLOWED_CHAT_ID", 0))

if not BOT_TOKEN:
    raise ValueError("Не найден TG_BOT_TOKEN в файле .env")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- MOCK STATE (Фейковое состояние для тестов) ---
# В реальном приложении бот будет делать GET-запрос в Selectel,
# но пока мы храним состояние в памяти.
MOCK_SERVER_IS_RUNNING = False

def get_keyboard():
    """Генерирует клавиатуру в зависимости от состояния сервера."""
    builder = InlineKeyboardBuilder()
    if not MOCK_SERVER_IS_RUNNING:
        builder.button(text="🟢 Запустить сервер", callback_data="cmd_start_server")
    else:
        builder.button(text="🔴 Остановить сервер", callback_data="cmd_stop_server")
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start. Проверяет права доступа."""
    if message.chat.id != ALLOWED_CHAT_ID:
        logging.warning(f"Несанкционированный доступ от {message.chat.id}")
        return await message.answer("⛔ У вас нет доступа к этому боту.")
    
    await message.answer(
        "👋 Привет! Я оркестратор сервера Minecraft.\n"
        "Выберите действие ниже:", 
        reply_markup=get_keyboard()
    )

@dp.callback_query(F.data == "cmd_start_server")
async def process_start_server(callback: types.CallbackQuery):
    """Мок процесса запуска сервера."""
    global MOCK_SERVER_IS_RUNNING
    
    # Защита от двойного клика
    if MOCK_SERVER_IS_RUNNING:
        return await callback.answer("Сервер уже запущен!", show_alert=True)
    
    # Редактируем сообщение, показывая процесс
    await callback.message.edit_text("⏳ [MOCK] Отправка запроса в API Selectel на создание VM...")
    
    # Имитируем ожидание создания сервера (5 секунд)
    await asyncio.sleep(2)
    await callback.message.edit_text("⏳ [MOCK] VM создана. Ожидание cloud-init и скачивания бекапа...")
    await asyncio.sleep(3)
    
    MOCK_SERVER_IS_RUNNING = True
    fake_ip = "192.168.99.150"
    
    # Отправляем результат и новую клавиатуру
    await callback.message.answer(
        f"✅ Сервер успешно запущен!\n"
        f"🌐 IP для подключения: `{fake_ip}`\n\n"
        f"Панель управления:",
        reply_markup=get_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer() # Закрываем "часики" на кнопке

@dp.callback_query(F.data == "cmd_stop_server")
async def process_stop_server(callback: types.CallbackQuery):
    """Мок процесса остановки сервера."""
    global MOCK_SERVER_IS_RUNNING
    
    if not MOCK_SERVER_IS_RUNNING:
        return await callback.answer("Сервер уже остановлен!", show_alert=True)
    
    await callback.message.edit_text("⏳ [MOCK] Подключение по SSH. Отправка сигнала остановки...")
    
    # Имитируем задержку на сохранение мира и выгрузку в Я.Диск
    await asyncio.sleep(3)
    await callback.message.edit_text("⏳ [MOCK] Выгрузка на Я.Диск завершена. Удаление VM из Selectel...")
    await asyncio.sleep(2)
    
    MOCK_SERVER_IS_RUNNING = False
    
    await callback.message.answer(
        "💾 [MOCK] Бекап сохранен, виртуальная машина и IP-адрес безвозвратно удалены.\n\n"
        "Панель управления:",
        reply_markup=get_keyboard()
    )
    await callback.answer()

async def main():
    logging.info("Запуск мок-бота...")
    # Пропускаем старые апдейты, чтобы бот не реагировал на то, что ему писали, пока он спал
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
