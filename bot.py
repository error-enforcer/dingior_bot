import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)


# ==========================================================
# НАЛАШТУВАННЯ
# Замініть посилання адміністраторів та посилання на відео.
# ==========================================================

ADMIN_LINKS = {
    "saksahanskoho": "https://t.me/dingiortattoo",
}


BOOKING_TEXT = """
👋 Привіт!

Для запису надішліть усі 3 пункти:
1. дату;
2. бажаний час;
3. номер телефону.

Адміністратор перевірить графік та підтвердить запис або запропонує найближче вільне віконце.
""".strip()


ADDRESS_TEXTS = {
    "saksahanskoho": """
📍 ЯК НАС ЗНАЙТИ

вул. Саксаганського, 7–12, 4-й поверх
🚇 Найзручніше від метро Палац спорту.

➡️ Вхід із двору. Після шлагбаума поверніть праворуч — перший під’їзд.
На домофоні натисніть 12В та піднімайтеся на 4-й поверх.

🎥 Відео, як нас знайти:
https://www.dingiortattoo.com/wp-content/uploads/2019/02/Route_to_studio0.mp4

❗ Термінала немає, тому бажано мати готівку.

Чекаємо на вас 🖤
""".strip(),
}


PRICE_TEXTS = {
    "piercing": """
💰 ПРАЙС НА ПІРСИНГ

Ціни вказані у форматі:
без прикраси • медсталь • титан

👂 Вуха

Мочка
500 • 600 • 650 грн

Дві мочки
850 • 1050 • 1150 грн

Helix / Scapha / Anti-Tragus
550 • 650 • 700 грн

Industrial / Orbital
600 • 750 • 850 грн

Tragus / Anti-Tragus
550 • 650 • 700 грн

Rook / Daith / Snug / Conch / Ragnar / Inner Pinna
550 • 650 • 700 грн

👃 Ніс та перенісся

Nostril — крило носа
550 • 650 • 700 грн

Septum / Nasallang
550 • 650 • 700 грн

Erl / Bridge / Third Eye
550 • 650 • 700 грн

👄 Губи та язик

Lip / Labret / Monroe / Medusa / Madonna
550 • 650 • 700 грн

Snake / Spider / Angel Bites
1100 • 1300 • 1400 грн

Smile / Anti-Smile
550 • 650 • 700 грн

Tongue / Symmetric Tongue / Frenulum
550 • 650 • 700 грн

✨ Обличчя та тіло

Антиброва
— • 950 • 1000 грн

Брова / Anti-Eyebrow / Eyelid
550 • 650 • 700 грн

Пупок
550 • 650 • 700 грн

Сосок
750 • — • 900 грн

Два соски
— • — • 1700 грн

💎 Мікродермали та тунелі

Мікродермал / Dermal Anchor
850 • — • 950 грн

Розтягування тунелів 4–10 мм
850 • — • 1000 грн

🛠 Додаткові послуги

Заміна прикраси — від 100 грн
Чищення проколу — 250 грн
Заміна накрутки мікродермалу — 300 грн
Чищення та видалення мікродермалу — 350 грн
Аплікаційне знеболення TKTX — 100 грн

Позначка «—» означає, що цей варіант не передбачений.
""".strip(),

    "tattoo": """
🎨 Ціни на татуювання

Мінімальна вартість — 1300 ГРН.

Кінцева ціна залежить від:
• розміру;
• складності ескізу;
• місця нанесення;
• тривалості роботи.

Для розрахунку надішліть адміністратору ескіз, розмір та місце нанесення.
""".strip(),

    "education": """
🎓 Ціни на навчання

• Навчання тату — https://www.dingiortattoo.com/shkola-tatujuvannja-ua/
• Навчання пірсингу — https://www.dingiortattoo.com/shkola-pircing-ua/

Деталі програми, тривалість і найближчі дати уточнюйте в адміністратора.
""".strip(),
}


CARE_TEXTS = {
    "tattoo": """
🎨 ДОГЛЯД ПІСЛЯ ТАТУЮВАННЯ

✅ Дотримуйтесь рекомендацій майстра та своєчасно змінюйте захисну плівку (за наявності).

🧼 Після зняття плівки мийте татуювання теплою водою з м’яким милом 2–3 рази на день та наносіть рекомендований крем.

❌ Не чухайте, не здирайте кірочки та не розпарюйте шкіру.

🚫 До повного загоєння уникайте басейнів, саун, водойм, інтенсивного засмагання та солярію.

👕 Носіть чистий, вільний одяг, який не натирає татуювання.

☀️ Після загоєння використовуйте сонцезахисний крем SPF 50, щоб зберегти яскравість татуювання.

📩 Якщо з’явилися сильний біль, виражений набряк або гнійні виділення — зв’яжіться з нашим майстром.

Більш детальна інструкція з догляду доступна за посиланням 👇

https://www.dingiortattoo.com/tattoo-kiev/
""".strip(),

    "piercing": """
💎 Догляд за пірсингом

1. Торкайтеся проколу лише чистими руками.
2. Обробляйте його засобом, рекомендованим майстром.
3. Не прокручуйте та не виймайте прикрасу самостійно.
4. Уникайте травмування місця проколу.
5. Не використовуйте спирт або перекис без рекомендації.

У разі сильного болю чи незвичної реакції напишіть майстру.
""".strip(),
}


SCHOOL_TEXTS = {
    "tattoo": """
🎨 Навчання тату

На курсі ви дізнаєтеся про:
• обладнання та матеріали;
• стерильність і безпеку;
• підготовку ескізу;
• техніки нанесення;
• роботу з моделями.

https://www.dingiortattoo.com/shkola-tatujuvannja-ua/
""".strip(),

    "piercing": """
💎 Навчання пірсингу

На курсі ви дізнаєтеся про:
• анатомію та види проколів;
• стерильність і безпеку;
• інструменти та прикраси;
• техніку виконання проколів;
• догляд після процедури.

https://www.dingiortattoo.com/shkola-pircing-ua/
""".strip(),
}


# ==========================================================
# КЛАВІАТУРИ
# ==========================================================

def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📝 Записатися", callback_data="menu:booking")],
            [InlineKeyboardButton("💰 Ціни", callback_data="menu:prices")],
            [InlineKeyboardButton("📍 Адреса", callback_data="menu:addresses")],
            [InlineKeyboardButton("🧴 Догляд", callback_data="menu:care")],
            [InlineKeyboardButton("🎓 Школа", callback_data="menu:school")],
        ]
    )


def booking_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📍 Саксаганського",
                    callback_data="booking:saksahanskoho",
                )
            ],
            [InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")],
        ]
    )


def prices_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💎 Пірсинг", callback_data="price:piercing")],
            [InlineKeyboardButton("🎨 Татуювання", callback_data="price:tattoo")],
            [InlineKeyboardButton("🎓 Навчання", callback_data="price:education")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")],
        ]
    )


def addresses_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📍 Саксаганського",
                    callback_data="address:saksahanskoho",
                )
            ],
            [InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")],
        ]
    )


def care_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎨 Татуювання", callback_data="care:tattoo")],
            [InlineKeyboardButton("💎 Пірсинг", callback_data="care:piercing")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")],
        ]
    )


def school_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎨 Навчання тату",
                    callback_data="school:tattoo",
                )
            ],
            [
                InlineKeyboardButton(
                    "💎 Навчання пірсингу",
                    callback_data="school:piercing",
                )
            ],
            [
                InlineKeyboardButton(
                    "💬 Задати питання",
                    callback_data="school:question",
                )
            ],
            [InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")],
        ]
    )


def back_keyboard(destination: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Назад", callback_data=destination)]]
    )


def admin_keyboard(
    admin_url: str,
    back_destination: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💬 Написати адміністратору",
                    url=admin_url,
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Назад",
                    callback_data=back_destination,
                )
            ],
        ]
    )


# ==========================================================
# КОМАНДИ
# ==========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        "Вітаємо! Оберіть потрібний розділ:",
        reply_markup=main_menu_keyboard(),
    )


async def menu_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        "Головне меню:",
        reply_markup=main_menu_keyboard(),
    )


# ==========================================================
# ОБРОБКА КНОПОК
# ==========================================================

async def handle_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    data = query.data

    if not isinstance(data, str):
        return

    if data == "menu:main":
        await query.edit_message_text(
            "Головне меню:",
            reply_markup=main_menu_keyboard(),
        )
        return

    if data == "menu:booking":
        await query.edit_message_text(
            "📝 Записатися\n\nОберіть адресу студії:",
            reply_markup=booking_keyboard(),
        )
        return

    if data == "menu:prices":
        await query.edit_message_text(
            "💰 Ціни\n\nОберіть потрібний розділ:",
            reply_markup=prices_keyboard(),
        )
        return

    if data == "menu:addresses":
        await query.edit_message_text(
            "📍 Адреса\n\nОберіть адресу студії:",
            reply_markup=addresses_keyboard(),
        )
        return

    if data == "menu:care":
        await query.edit_message_text(
            "🧴 Догляд\n\nОберіть потрібний розділ:",
            reply_markup=care_keyboard(),
        )
        return

    if data == "menu:school":
        await query.edit_message_text(
            "🎓 Школа\n\nОберіть потрібний розділ:",
            reply_markup=school_keyboard(),
        )
        return

    if data.startswith("booking:"):
        location = data.split(":", maxsplit=1)[1]
        admin_url = ADMIN_LINKS.get(location)

        if not admin_url:
            await query.edit_message_text(
                "Не вдалося знайти дані адміністратора.",
                reply_markup=back_keyboard("menu:booking"),
            )
            return

        await query.edit_message_text(
            BOOKING_TEXT,
            reply_markup=admin_keyboard(
                admin_url,
                "menu:booking",
            ),
        )
        return

    if data.startswith("price:"):
        category = data.split(":", maxsplit=1)[1]
        text = PRICE_TEXTS.get(category)

        if text:
            await query.edit_message_text(
                text,
                reply_markup=back_keyboard("menu:prices"),
            )
        return

    if data.startswith("address:"):
        location = data.split(":", maxsplit=1)[1]
        text = ADDRESS_TEXTS.get(location)

        if text:
            await query.edit_message_text(
                text,
                reply_markup=back_keyboard("menu:addresses"),
                disable_web_page_preview=True,
            )
        return

    if data.startswith("care:"):
        category = data.split(":", maxsplit=1)[1]
        text = CARE_TEXTS.get(category)

        if text:
            await query.edit_message_text(
                text,
                reply_markup=back_keyboard("menu:care"),
                disable_web_page_preview=True,
            )
        return

    if data.startswith("school:"):
        category = data.split(":", maxsplit=1)[1]

        if category in SCHOOL_TEXTS:
            await query.edit_message_text(
                SCHOOL_TEXTS[category],
                reply_markup=back_keyboard("menu:school"),
            )
            return

        if category == "question":
            await query.edit_message_text(
                "💬 Задати питання\n\n"
                "Напишіть адміністратору своє питання щодо навчання. "
                "Вам повідомлять програму, вартість та найближчі доступні дати.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "💬 Написати адміністратору",
                                url=ADMIN_LINKS["saksahanskoho"],
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "⬅️ Назад",
                                callback_data="menu:school",
                            )
                        ],
                    ]
                ),
            )
            return

    await query.edit_message_text(
        "Цей пункт меню недоступний.",
        reply_markup=main_menu_keyboard(),
    )


# ==========================================================
# ЗВИЧАЙНІ ТЕКСТОВІ ПОВІДОМЛЕННЯ
# ==========================================================

async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        "Оберіть потрібний розділ за допомогою кнопок:",
        reply_markup=main_menu_keyboard(),
    )


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logging.error(
        "Помилка під час обробки повідомлення",
        exc_info=context.error,
    )


# ==========================================================
# ЗАПУСК
# ==========================================================

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "Не знайдено змінну середовища TELEGRAM_BOT_TOKEN."
        )

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(handle_button))

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text,
        )
    )

    application.add_error_handler(error_handler)

    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
