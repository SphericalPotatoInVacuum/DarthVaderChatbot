from loguru import logger
import os

import openai
import toml
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, MessageHandler, ContextTypes

from models import DialogueEntry, Base


class OpenAIConfig(BaseModel):
    model: str
    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    stop: list[str]


openai.api_key = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_DB = os.getenv("DB_DB")


logger.add('log.log', rotation='100 MB')

config = toml.load('configs/config.toml')
oaiconfig = OpenAIConfig(**config['openai'])

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@database/{DB_DB}", echo=True, future=True)
Base.metadata.create_all(engine)


async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user is None:
        return

    session = Session(engine)
    row = session.execute(
        select(DialogueEntry)
        .where(DialogueEntry.user_id == update.effective_user.id)
        .order_by(DialogueEntry.entry_id)
    ).first()
    previous_entry = None if row is None else row[0]
    previous_entry_id = 0 if previous_entry is None else previous_entry.entry_id

    context_rows = session.execute(
        select(DialogueEntry.exchange)
        .where(DialogueEntry.user_id == update.effective_user.id)
        .order_by(DialogueEntry.entry_id)
    ).all()

    chat_context = '\n'.join([row[0] for row in context_rows])
    added_context = config["restart_sequence"] + update.effective_message.text + config["start_sequence"]

    response = openai.Completion.create(
        prompt=chat_context + added_context,
        **oaiconfig.dict(),
    )

    if response is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Something broke, we will fix it soon")
        return

    response_text = response['choices'][0]['text']

    entry = DialogueEntry(
        user_id=update.effective_user.id,
        entry_id=previous_entry_id + 1,
        exchange=added_context + response_text
    )
    session.add(entry)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

    session.commit()
    session.close()

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    query_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), query)
    application.add_handler(query_handler)

    application.run_polling()
