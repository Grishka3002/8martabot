import asyncio
import logging
import os
import random
from pathlib import Path

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


BASE_DIR = Path(__file__).resolve().parent
PHOTO_DIR = BASE_DIR
ONBOARD_PHOTO = BASE_DIR / "OnboardMessage.png"

PEOPLE = {
    "Максим": "Max",
    "Ильич": "Ilich",
    "Ваня Ненашев": "VanyaN",
    "Ваня Столбоушкин": "VanyaS",
    "Гриша": "Grisha",
    "Вадик": "Vadik",
    "Влад": "Vlad",
}

RANDOM_BUTTON = "Рандом"

PHOTO_CAPTIONS = {
    "Max": {
        "Max_1.png": "Гуляя по лесу в праздник, помни о енотах!",
        "Max_2.png": "Поздравляем самых гламурных дам, в самый почти мужской праздник",
        "Max_3.png": "В такой прекрасный праздник, хочу чтобы всем достались букеты, которые они заслужили! И тебе, конечно же, тоже 🌹",
    },
    "Ilich": {
        "Ilich_1.png": "Желаю чтобы всегда, не придумал ещё, 🤣🤣",
        "Ilich_2.png": "Желаю чтобы всегда были в безопасности",
        "Ilich_3.png": "Желаю чтобы всегда высыпались)",
    },
    "VanyaN": {
        "VanyaN_1.png": "Оставайтесь нашими приятными витаминками для глаз",
        "VanyaN_2.png": "Будьте вечным двигателем нашего восхищения",
        "VanyaN_3.png": "Спасибо, что переносите нашу жизнь с «жёсткого диска» реальности на «мягкое облако» счастья",
    },
    "VanyaS": {
        "VanyaS_1.png": "Рафаэль уже не тот, но Сикстинскую капеллу бы с тебя написал",
        "VanyaS_2.png": "Ты конечно не кубок, но твое сердечко я бы тоже не против завоевать",
        "VanyaS_3.png": "Ого, это что за ляля на меня смотрит?😍 Да ты шооо.\nС праздником, тигрица🐅",
    },
    "Grisha": {
        "Grisha_1.png": "Красотка, с 8 Марта тебя! Желаю тебе всегда быть такой же яркой и солнечной\nкак новогодняя елочка в конце января🌞",
        "Grisha_2.png": "Ну ты вообще, красотка! Вот чтобы у тебя всегда было что-нибудь кчаю",
        "Grisha_3.png": "Солнце, желаю тебе не сидеть....сложа руки)",
    },
    "Vadik": {
        "Vadik_1.png": "Если бы у тебя был QR‑код, он бы вёл прямиком к моему сердечку 💘\nС 8 Марта, моя самая топовая ссылка 😏📲",
        "Vadik_2.png": "Ты чё там без меня обсуждаешь, принцесса? 👀\nС 8 Марта, моя главная тема для сплетен 😘",
        "Vadik_3.png": "Вот я, комплект \"для твоего идеального вечера\": я, сок и чуть-чуть градуса 😎🍑\nС 8 Марта, королева весёлых ночей 💃✨",
    },
    "Vlad": {
        "Vlad_1.png": "Хорошо, что я не родился девушкой, потому что не сравнился бы с тобой 100%",
        "Vlad_2.png": "Любим Вас, даже, если выглядим как клоуны!",
        "Vlad_3.png": "Красотка, помни, что не только в этот день протяну тебе руку помощи! С праздником)",
    },
}

KEYBOARD = ReplyKeyboardMarkup(
    [
        ["Максим", "Ильич"],
        ["Ваня Ненашев", "Ваня Столбоушкин"],
        ["Гриша", "Вадик"],
        ["Влад", RANDOM_BUTTON],
    ],
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = """С 8 Марта тебя! 💐
Сегодня мы, одинокие волки молодёжки 🐺, решили, что нельзя оставить без поздравления ни одну девушку.

Мы хотели поздравить каждую. Да-да, каждую!
Но нас меньше, чем вас…
Поэтому мы придумали этот бот —
чтобы дотянуться до всех и до каждой ✨

И вот что тебя ждёт:
Каждый из нас подготовил по ТРИ поздравления 😎
Так что твоя миссия —
🎁 тыкать, пока не соберёшь всю коллекцию, как в киндер-сюрпризе!

Не знаешь, кого выбрать?
Жми кнопку «Рандом» — судьба решит за тебя 🎲

Соберёшь всё — получишь +100 к настроению, +1000 к весне и +∞ к улыбке 🌷

Ну что, начинаем охоту за поздравлениями? 🐺✨"""

    if ONBOARD_PHOTO.exists():
        with ONBOARD_PHOTO.open("rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=welcome_text,
                reply_markup=KEYBOARD,
            )
        return

    await update.message.reply_text(welcome_text, reply_markup=KEYBOARD)


def get_random_photo(person_name: str) -> tuple[Path, str]:
    folder_name = PEOPLE[person_name]
    person_folder = PHOTO_DIR / folder_name

    files = [file for file in person_folder.iterdir() if file.is_file()]
    if not files:
        raise FileNotFoundError(f"В папке {person_folder} нет фотографий")

    photo_path = random.choice(files)
    caption = PHOTO_CAPTIONS.get(folder_name, {}).get(photo_path.name, photo_path.stem)
    return photo_path, caption


async def send_person_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    person_name = update.message.text
    if person_name == RANDOM_BUTTON:
        person_name = random.choice(list(PEOPLE))

    if person_name not in PEOPLE:
        await update.message.reply_text("Нажми одну из кнопок на клавиатуре.")
        return

    try:
        photo_path, caption = get_random_photo(person_name)
    except FileNotFoundError as error:
        await update.message.reply_text(str(error))
        return

    with photo_path.open("rb") as photo:
        await update.message.reply_photo(photo=photo, caption=caption)


def main() -> None:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не найден BOT_TOKEN в .env")

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_person_photo))
    asyncio.set_event_loop(asyncio.new_event_loop())
    application.run_polling()


if __name__ == "__main__":
    main()
