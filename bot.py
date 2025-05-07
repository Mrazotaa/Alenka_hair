
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")

ASK_PREVIOUS = 0
ASK_CAPSULES_OR_LENGTH = 1
ASK_DENSITY = 2
ASK_DESIRED_LENGTH = 3

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['Да', 'Нет']]
    await update.message.reply_text(
        "Привет! Я помогу рассчитать стоимость наращивания волос. Наращивали ли вы раньше волосы?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_PREVIOUS

async def ask_capsules_or_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    user_data[update.effective_chat.id] = {'previous_extension': answer}

    if answer == 'Да':
        await update.message.reply_text("Сколько капсул или грамм использовалось?")
    else:
        reply_keyboard = [['Волосы закрывают только уши', 'Выше плеч', 'Ниже плеч, но выше лопаток',
                           'Ниже лопаток', 'По талию']]
        await update.message.reply_text("Какая исходная длина ваших волос?",
                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_CAPSULES_OR_LENGTH

async def ask_density(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_chat.id]['length_or_capsules'] = update.message.text
    reply_keyboard = [['Очень густые', 'Средней густоты', 'Редкие волосы']]
    await update.message.reply_text("Какова густота ваших волос?",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_DENSITY

async def ask_desired_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_chat.id]['density'] = update.message.text
    reply_keyboard = [['Загустить только височные зоны', 'Загустить исходную длину своих волос',
                       'Волосы по лопатки/по грудь 45 см', 'Волосы ниже лопаток 50-55 см', 'Волосы по талию 60 см']]
    await update.message.reply_text("Какой длины волосы вы хотите?",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_DESIRED_LENGTH

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_chat.id]['desired_length'] = update.message.text
    data = user_data[update.effective_chat.id]

    price = "Требуется индивидуальный расчёт"
    time = "—"

    combos = {
        ("Волосы закрывают только уши", "Очень густые", "Загустить только височные зоны"): ("10.000-15.000₽", "1-1.5 часа"),
        ("Волосы закрывают только уши", "Очень густые", "Загустить исходную длину своих волос"): ("10.000-15.000₽", "1-1.5 часа"),
        ("Волосы закрывают только уши", "Очень густые", "Волосы по лопатки/по грудь 45 см"): ("30.000-35.000₽", "3 часа"),
        ("Волосы закрывают только уши", "Очень густые", "Волосы ниже лопаток 50-55 см"): ("40.000-45.000₽", "4-5 часов"),
        ("Волосы закрывают только уши", "Очень густые", "Волосы по талию 60 см"): ("50.000₽", "5 часов"),
        ("Выше плеч", "Очень густые", "Загустить только височные зоны"): ("10.000₽", "1 час"),
        ("Выше плеч", "Очень густые", "Загустить исходную длину своих волос"): ("10.000₽", "1-1.5 часа"),
        ("Выше плеч", "Очень густые", "Волосы по лопатки/по грудь 45 см"): ("30.000-35.000₽", "3-3.5 часа"),
        ("Выше плеч", "Очень густые", "Волосы ниже лопаток 50-55 см"): ("35.000-40.000₽", "3-4 часа"),
        ("Выше плеч", "Очень густые", "Волосы по талию 60 см"): ("40.000₽", "4-5 часов"),
        ("Ниже плеч, но выше лопаток", "Очень густые", "Загустить только височные зоны"): ("10.000₽", "1-1.5 часа"),
        ("Ниже плеч, но выше лопаток", "Очень густые", "Загустить желаемую длину волос"): ("10.000-15.000₽", "1.5-2 часа"),
        ("Ниже плеч, но выше лопаток", "Очень густые", "Волосы по лопатки/по грудь 45 см"): ("30.000₽", "2-3 часа"),
        ("Ниже плеч, но выше лопаток", "Очень густые", "Волосы ниже лопаток 50-55 см"): ("30.000-35.000₽", "3-4 часа"),
        ("Ниже плеч, но выше лопаток", "Очень густые", "Волосы по талию 60 см"): ("35.000-40.000₽", "4-5 часов"),
    }

    combo_key = (data.get('length_or_capsules'), data.get('density'), data.get('desired_length'))
    if combo_key in combos:
        price, time = combos[combo_key]

    await update.message.reply_text(f"💰 Ориентировочная стоимость: {price}
⏱ Время работы: {time}")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_PREVIOUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_capsules_or_length)],
            ASK_CAPSULES_OR_LENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_density)],
            ASK_DENSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_desired_length)],
            ASK_DESIRED_LENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    print("Бот запущен...")
    app.run_polling()
