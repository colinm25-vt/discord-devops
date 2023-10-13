from helpers.embedhelper import build_embed, EmbedField
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from typing import Union, Dict
from enum import Enum
import nextcord


class MeetingCog(commands.Cog):
    """
    Meeting command cog

    Commands
    --------
    meeting
    """

    def __init__(self, client: nextcord.Client):
        self.client: nextcord.Client = client

    @nextcord.slash_command(name="meeting", description="Meeting commands")
    async def _meeting(self, interaction: Interaction):
        await interaction.send("Master command", ephemeral=True)

    @_meeting.subcommand(name="add", description="Add a meeting")
    async def _mt_add(self, interaction: Interaction):
        await interaction.send("Not implemented.")
