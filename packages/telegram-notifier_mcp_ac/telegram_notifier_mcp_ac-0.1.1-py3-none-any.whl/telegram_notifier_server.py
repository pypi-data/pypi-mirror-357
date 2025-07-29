import os
import requests
from dotenv import *
from mcp.server.fastmcp import FastMCP
from datetime import datetime


load_dotenv() # Load environment variables from .env file

TELEGRAM_BOT_TOKEN = os.environ.get("AC_TG_KEY")
TELEGRAM_CHAT_ID = os.environ.get("AC_TG_CHATID")


mcp = FastMCP("test_mcp")

@mcp.tool()
def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

# @mcp.tool()
# def send_message(message: str):
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     payload = {
#         "chat_id": TELEGRAM_CHAT_ID,
#         "text": message
#     }
#     response = requests.post(url, data=payload)
#     return response.json()

mcp.run(transport="stdio")