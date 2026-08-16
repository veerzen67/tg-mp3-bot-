import asyncio
import os
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart

# -------------------------------------------------------------
# 1. Запуск фейкового веб-сервера для Render (чтобы не закрывал бот)
# -------------------------------------------------------------
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# -------------------------------------------------------------
# 2. Настройки бота
# -------------------------------------------------------------
TOKEN = os.environ.get("BOT_TOKEN", "8869463639:AAH-Eo0h258B8p_YcfTiR-CtP0-Z0ZCVnsk")
ALLOWED_USERS = [1117053098, 6461846641]


bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:

        await message.answer("🔒 Доступ ограничен.")
        return
    await message.answer("👋 Привет! Отправь мне видео, и я извлеку из него MP3.")

# -------------------------------------------------------------
# 3. Конвертация видео в MP3
# -------------------------------------------------------------
@dp.message(F.video)
async def convert_video_to_mp3(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:

        return

    status_msg = await message.answer("⏳ Скачиваю видео...")
    
    file_id = message.video.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    
    input_video = f"video_{message.from_user.id}.mp4"
    output_audio = f"audio_{message.from_user.id}.mp3"
    
    await bot.download_file(file_path, input_video)
    
    await status_msg.edit_text("⚙️ Конвертирую в MP3...")
    
    # Используем ffmpeg для конвертации
    cmd = f"ffmpeg -i {input_video} -vn -ar 44100 -ac 2 -b:a 192k {output_audio} -y"
    subprocess.run(cmd, shell=True, check=True)
    
    await status_msg.edit_text("Преобразую в аудиофайл...")
    
    audio_file = types.FSInputFile(output_audio)
    await message.answer_audio(audio_file, caption="Вот твое аудио! 🎵")
    
    # Удаляем временные файлы
    if os.path.exists(input_video):
        os.remove(input_video)
    if os.path.exists(output_audio):
        os.remove(output_audio)
    
    await status_msg.delete()

# -------------------------------------------------------------
# 4. Запуск
# -------------------------------------------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

