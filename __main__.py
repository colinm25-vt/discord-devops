import helpers.simplelogging as logger
from dotenv import load_dotenv
import nextcord
import os

from cogs.pingcog import PingCog
from cogs.kanbancog import KanbanCog
from cogs.meetingcog import MeetingCog


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
INTENTS = nextcord.Intents.none()


def prep_client():
    global client
    client = nextcord.Client(intents=INTENTS)
    client.add_cog(PingCog(client))
    client.add_cog(KanbanCog(client))
    client.add_cog(MeetingCog(client))

    @client.event
    async def on_ready():
        logger.log(f"Client connected as {client.user}.")
        await client.change_presence(activity=nextcord.Game(name="with code"))


def client_handler():
    """Start the client, use a keyboard interrupt to close"""
    logger.log("Use ctrl+C to shut down.")
    prep_client()
    client.run(DISCORD_TOKEN)
    logger.log("Shutting down handler.")


if __name__ == "__main__":
    client_handler()
