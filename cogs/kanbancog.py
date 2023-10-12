from helpers.embedhelper import build_embed, EmbedField
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from typing import Union, Dict
from enum import Enum
import nextcord


class TicketStatus (Enum):
    NEW = "New"
    IN_PROGRESS = "In progress"
    IN_REVIEW = "In review"
    DONE = "Done"


class Ticket:
    def __init__(self, id: int, name: str, desc: str, status: TicketStatus = TicketStatus.NEW, assignee: Union[str, None] = None):
        self.id: int = id
        self.name: str = name
        self.desc: str = desc
        self.status: TicketStatus = status
        self.assignee: Union[str, None] = assignee

    def get_assignee(self) -> str:
        return self.assignee if self.assignee is not None else "None"

    def embed(self) -> nextcord.Embed:
        fields = [
            EmbedField("Description", self.desc),
            EmbedField("Status", self.status.value),
            EmbedField(
                "Assignee", self.get_assignee())
        ]
        return build_embed(*fields, title=f"{self.id} - {self.name}")

    def embed_field(self) -> EmbedField:
        return EmbedField(f"{self.id} - {self.name}", f"Status: {self.status.value}\nAssignee: {self.get_assignee()}")


class KanbanCog (commands.Cog):
    '''
    Kanban command cog

    Commands
    --------
    kanban (+6)
    '''

    def __init__(self, client: nextcord.Client):
        self.client: nextcord.Client = client
        self.tickets: Dict[int, Ticket] = dict()
        self.next_ticket_id = 1  # never decrements

    @nextcord.slash_command(name="kanban", description="Kanban board commands")
    async def _kanban(self, interaction: Interaction):
        await interaction.send("Master command", ephemeral=True)

    @_kanban.subcommand(name="add", description="Add a ticket")
    async def _kb_add(self, interaction: Interaction, name: str, description: str):
        self.tickets[self.next_ticket_id] = Ticket(
            self.next_ticket_id, name, description)
        self.next_ticket_id += 1
        await interaction.send(f"Ticket added! Id: {self.next_ticket_id - 1}")

    @_kanban.subcommand(name="remove", description="Remove a ticket")
    async def _kb_remove(self, interaction: Interaction, id: int):
        try:
            del self.tickets[id]
        except KeyError:
            await interaction.send("No such ticket.", ephemeral=True)
        else:
            await interaction.send("Ticket removed!")

    @_kanban.subcommand(name="assign", description="Assign a ticket")
    async def _kb_assign(self, interaction: Interaction, id: int, name: str):
        try:
            self.tickets[id].assignee = name
        except KeyError:
            await interaction.send("No such ticket.", ephemeral=True)
        else:
            await interaction.send("Ticket updated!")

    @_kanban.subcommand(name="move", description="Move a ticket")
    async def _kb_move(self, interaction: Interaction, id: int, status: str = SlashOption("status", choices=[e.value for e in TicketStatus])):
        try:
            self.tickets[id].status = TicketStatus(status)
        except KeyError:
            await interaction.send("No such ticket.", ephemeral=True)
        else:
            await interaction.send("Ticket updated!")

    @_kanban.subcommand(name="get", description="Get info about a ticket")
    async def _kb_get(self, interaction: Interaction, id: int):
        try:
            await interaction.send(embed=self.tickets[id].embed())
        except KeyError:
            await interaction.send("No such ticket.", ephemeral=True)

    @_kanban.subcommand(name="list", description="List all tickets")
    async def _kb_list(self, interaction: Interaction):
        # TODO: there is a maximum of 10 fields per embed, break this into multiple pages
        fields = [self.tickets[i].embed_field() for i in self.tickets.keys()]
        embed = build_embed(*fields, title="Tickets")
        await interaction.send(embed=embed)
