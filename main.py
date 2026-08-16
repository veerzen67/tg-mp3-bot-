import asyncio
import os
import subprocess
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart

TOKEN = "8869463639:AAH-Eo0h258B8p_YcfTiR-CtP0-Z0ZCVnsk"
ALLOWED_USER_ID = 1117053098

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        await message.answer("🔒 Доступ ограничен. Этот бот приватный.")
        return
    await message.answer("👋 Привет! Отправь мне видео (до 20 МБ), и я сделаю из него MP3.")

@dp.message(F.video)
async def convert_video_to_mp3(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return

    status_msg = await message.answer("⏳ Скачиваю видео и обрабатываю звук...")
    
    video_file = await bot.get_file(message.video.file_id)
    input_path = f"video_{message.from_user.id}.mp4"
    output_path = f"audio_{message.from_user.id}.mp3"
    
    try:
        await bot.download_file(video_file.file_path, input_path)
        
        process = subprocess.run([
            'ffmpeg', '-i', input_path, 
            '-vn', '-acodec', 'libmp3lame', 
            '-ab', '192k', '-y', output_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if process.returncode == 0 and os.path.exists(output_path):
            audio_file = types.FSInputFile(output_path, filename=f"{message.video.file_name or 'audio'}.mp3")
            await message.answer_audio(audio=audio_file, caption="Готово! 🎵")
        else:
            await message.answer("❌ Ошибка сжатия файла сервером.")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        
    finally:
        await status_msg.delete()
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
