import os
import json
import urllib.request
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("telegram-mcp")

# Par défaut, utilise les identifiants fournis pour le développement
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8768150508:AAG3Wdf3XoIvuebkMF6jEhav5FvsRxhvtWg")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8631997648")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="send_telegram_message",
            description="Envoie un message texte via le bot Telegram",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Le texte du message à envoyer"
                    }
                },
                "required": ["text"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "send_telegram_message":
        raise ValueError(f"Outil inconnu: {name}")

    text = arguments.get("text")
    if not text:
        raise ValueError("L'argument 'text' est requis")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            if result.get("ok"):
                msg_id = result['result']['message_id']
                return [TextContent(type="text", text=f"Message envoyé avec succès. Message ID: {msg_id}")]
            else:
                return [TextContent(type="text", text=f"Erreur de l'API Telegram: {result.get('description')}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Échec de l'envoi du message: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
