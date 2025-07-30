import asyncio
import logging
from aiogram import (
    Bot,
    Dispatcher,
    types,
    enums
)
from aiogram.filters import Command
from smolagents import (
    OpenAIServerModel,
    ToolCallingAgent,
    DuckDuckGoSearchTool
)
from python_llm_assistant.prompts import SYSTEM_PROMPT
from python_llm_assistant.config import (
    BOT_TOKEN,
    TOGETHER_API,
    VERSION
)

import inspect, os, sys
print("MODULE __main__.py loaded from:", inspect.getsourcefile(inspect.getmodule(inspect.currentframe())))
print("sys.path:", sys.path)

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Model initialization
model = OpenAIServerModel(
    model_id='meta-llama/Llama-3.3-70B-Instruct-Turbo-Free',
    api_base='https://api.together.xyz/v1/',
    api_key=TOGETHER_API
)

web_search = DuckDuckGoSearchTool(max_results=3)
agent = ToolCallingAgent(
    model=model,
    tools=[web_search]
)
agent.prompt_templates["system_prompt"] = SYSTEM_PROMPT


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handler for /start command"""
    await message.answer(
        "Привет! Я ваш умный ассистент. "
        "Я могу отвечать на вопросы и искать информацию в интернете. "
        "Просто задайте мне любой вопрос!"
    )


@dp.message()
async def handle_message(message: types.Message):
    """Handler for all messages"""
    await message.chat.do(enums.ChatAction.TYPING)
    
    try:
        response = await asyncio.to_thread(agent.run, message.text)
        await message.answer(response)
    except Exception as e:
        await message.answer(
            "Извините, произошла ошибка при обработке вашего запроса. "
            "Пожалуйста, попробуйте еще раз позже."
        )
        print(f"Error: {e}")


async def main():
    """Main function to start the bot"""
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
