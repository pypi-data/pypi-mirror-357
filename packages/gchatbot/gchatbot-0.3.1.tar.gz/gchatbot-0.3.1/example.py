# example.py
import os
import asyncio
from typing import Any, Dict
from fastapi import FastAPI, Request, BackgroundTasks
from gchatbot import GChatBot, ExtractedEventData, EventPayload, ResponseType

# Ensure you have a 'service.json' file or set the environment variable.
SERVICE_ACCOUNT_FILE: str = os.environ.get("SERVICE_ACCOUNT_FILE", "service.json")

class ExampleBot(GChatBot):
    """
    An example bot demonstrating synchronous and asynchronous methods.
    
    This example shows how you can mix sync and async methods in the same
    class, and the library will automatically detect and handle each appropriately.
    It also demonstrates serverless-safe progressive responses.
    """
    def __init__(self) -> None:
        super().__init__(
            botName="Hybrid Example Bot",
            serviceAccountFile=SERVICE_ACCOUNT_FILE,
        )

    async def _processSlashCommand(self, command: str, arguments: str, extractedData: ExtractedEventData, eventData: EventPayload) -> ResponseType:
        """
        ASYNCHRONOUS METHOD - Processes slash commands using async/await.
        This method is async, so it can use `await` for non-blocking operations.
        
        Args:
            command: The command name without the leading '/'.
            arguments: The arguments provided after the command.
            extractedData: Structured data extracted from the event payload.
            eventData: The original event payload from Google Chat.
            
        Returns:
            str: A simple string response.
            OR Tuple[str, Awaitable[str]]: A progressive response (quick + detailed).
        """
        user: str = extractedData.get('userDisplayName', 'User')
        userChatId: str = extractedData.get('userGoogleChatId', 'Unknown ID')
        
        if command == "long_task":
            # Demonstrates a serverless-safe progressive response.
            quickResponse = f"✅ Okay, {user}. I've started your long task. I will update this message when it's done."
            
            async def detailedResponse() -> str:
                await asyncio.sleep(8)  # Simulates a long-running API call or data processing.
                return f"🎉 Task complete for {user}! The results are ready."
            
            # Returning a tuple triggers the progressive response mechanism.
            return (quickResponse, detailedResponse())
        
        elif command == "info":
            # Demonstrates accessing the extracted event data.
            userEmail: str = extractedData.get('userEmail', 'Unknown Email')
            spaceName: str = extractedData.get('spaceName', 'Unknown Space')
            isDM: bool = extractedData.get('isDirectMessageEvent', False)
            
            return f"""ℹ️ *User and Context Info:*

*User:*
• Name: {user}
• Email: {userEmail}
• Google Chat ID: {userChatId}

*Space:*
• Name: {spaceName}
• Type: {'Direct Message (DM)' if isDM else 'Room/Group'}"""
        
        else:
            await asyncio.sleep(0.5)
            return f"✅ Unknown ASYNC command `/{command}` executed for {user}."

    def _processMessage(self, text: str, extractedData: ExtractedEventData, eventData: EventPayload) -> ResponseType:
        """
        SYNCHRONOUS METHOD - Processes regular messages using standard blocking calls.
        
        Args:
            text: The processed text from the message.
            extractedData: Structured data extracted from the event payload.
            eventData: The original event payload from Google Chat.
            
        Returns:
            str: A simple string response.
            OR Tuple[str, Awaitable[str]]: A progressive response (quick + detailed).
        """
        user: str = extractedData.get('userDisplayName', 'User')
        
        if "help" in text.lower():
            return f"Hi {user}. I'm a demo bot. Try the slash commands `/long_task` or `/info`."
        
        else:
            return f"💬 SYNC message processed for {user}: '{text}'"

# --- FastAPI App Setup ---
app: FastAPI = FastAPI(title="gchatbot Hybrid Example")
bot: ExampleBot = ExampleBot()

@app.post("/webhook")
async def handleEvent(request: Request, backgroundTasks: BackgroundTasks) -> Any:
    """
    The main entry point for all Google Chat events.
    This function receives the `backgroundTasks` object from FastAPI
    and passes it to the GChatBot library.
    
    Args:
        request: The FastAPI HTTP request object containing the event payload.
        backgroundTasks: The FastAPI background tasks manager, injected by the framework.
        
    Returns:
        A JSON response for Google Chat.
    """
    return await bot.handleRequest(request, backgroundTasks)

@app.get("/")
def home() -> Dict[str, Any]:
    """
    A simple health-check endpoint.
    """
    return {
        "status": "active", 
        "bot_name": bot.botName, 
        "info": "This bot demonstrates both async and sync command handling.",
        "commands": [
            "/long_task - A slow command that uses a progressive response.",
            "/info - A quick command that shows user and space details."
        ]
    }

# To run locally: uvicorn example:app --reload --port 8080