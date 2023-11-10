from helpers.buttonviews import ConfirmButtons, ButtonEnums
from helpers.embedhelper import build_embed, EmbedField
from nextcord import Interaction, SlashOption
from typing import Union, Dict, List
from nextcord.ext import commands
from datetime import datetime
import nextcord


timeopt = SlashOption(description="(mm/dd(/yy)) hh:mm ({a,p}m) where () = optional and {} = choose either")


def parse_timeopt(tm: str) -> Union[datetime, None]:
    tm = tm.upper()
    try:
        return datetime.strptime(tm, "%m/%d/%y %I:%M %p")
    except ValueError:
        try:
            return datetime.strptime(tm, "%m/%d/%y %H:%M")
        except ValueError:
            try:
                out = datetime.strptime(tm, "%m/%d %H:%M")
                cur = datetime.now()
                out = out.replace(year=cur.year)
                return out
            except ValueError:
                try:
                    out = datetime.strptime(tm, "%m/%d %I:%M %p")
                    cur = datetime.now()
                    out = out.replace(year=cur.year)
                    return out
                except ValueError:
                    try:
                        out = datetime.strptime(tm, "%I:%M %p")
                        cur = datetime.now()
                        out = out.replace(day=cur.day, month=cur.month, year=cur.year)
                        return out
                    except ValueError:
                        try:
                            out = datetime.strptime(tm, "%H:%M")
                            cur = datetime.now()
                            out = out.replace(day=cur.day, month=cur.month, year=cur.year)
                            return out
                        except ValueError:
                            return None


class TimeBlock:
    def __init__(self, start: datetime, end: datetime):
        if start >= end:
            raise ValueError("start must be before end")
        self.start = start
        self.end = end

    def overlaps(self, other: "TimeBlock") -> bool:
        if not isinstance(other, TimeBlock):
            return False
        return self.start <= other.end or self.end >= other.start

    def _get_ts_str(self) -> str:
        cur = datetime.now()
        if (
            self.start.year == self.end.year
            and self.start.month == self.end.month
            and self.start.day == self.end.day
            and self.start.year == cur.year
            and self.start.month == cur.month
            and self.start.day == cur.day
        ):
            return "%-I:%M %p"
        return "%-m/%-d/%y %-I:%M %p"

    def __str__(self) -> str:
        return f"{self.start.strftime(self._get_ts_str())} - {self.end.strftime(self._get_ts_str())}"


class MeetingUser:
    def __init__(self, user: nextcord.Member):
        self.user = user
        self.timeblocks: List[TimeBlock] = []


class Meeting:
    def __init__(self, timeblock: TimeBlock):
        self.timeblock = timeblock
        self.users: List[MeetingUser] = []
        self.valid = True

    def __str__(self) -> str:
        return f"{self.timeblock}"

    def register_user(self, user: MeetingUser) -> bool:
        if not self.valid:
            return False
        if user in self.users:
            return True
        for tb in user.timeblocks:
            if self.timeblock.overlaps(tb):
                return False
        self.users.append(user)
        user.timeblocks.append(self.timeblock)
        return True

    def deregister_user(self, user: MeetingUser) -> bool:
        if not self.valid:
            return False
        for u in self.users:
            if u is user:
                self.users.remove(u)
                user.timeblocks.remove(self.timeblock)
                return True
        return False

    def teardown(self):
        for u in self.users:
            self.deregister_user(u)
        self.valid = False


class MeetingCog(commands.Cog):
    """
    Meeting command cog

    Commands
    --------
    meeting (+5)
    """

    def __init__(self, client: nextcord.Client):
        # TODO: users should be able to un-busy themselves
        #       also, we'd need a way to keep track of who is in what meeting - reference meetings in MeetingUser?
        #       remember to update that information if meetings are canceled
        # TODO: users should be able to view the meetings they have RSVP'd to
        self.client: nextcord.Client = client
        self.meetings: Dict[int, Meeting] = {}
        self.next_meeting_id = 1
        self.users: Dict[nextcord.Member, MeetingUser] = {}

    def _get_user(self, user: nextcord.Member) -> MeetingUser:
        if user not in self.users:
            self.users[user] = MeetingUser(user)
        return self.users[user]

    @nextcord.slash_command(name="meeting", description="Meeting commands")
    async def _meeting(self, interaction: Interaction):
        await interaction.send("Master command", ephemeral=True)

    @_meeting.subcommand(name="schedule", description="Schedule a meeting")
    async def _mt_add(self, interaction: Interaction, start: str = timeopt, end: str = timeopt):
        st = parse_timeopt(start)
        en = parse_timeopt(end)
        if st is None or en is None:
            await interaction.send("Invalid format - see hint in description.", ephemeral=True)
            return
        if st >= en:
            await interaction.send("Start time must come before end time.", ephemeral=True)
            return
        self.meetings[self.next_meeting_id] = Meeting(TimeBlock(st, en))
        self.next_meeting_id += 1
        await interaction.send(f"Added meeting {self.next_meeting_id - 1}: {self.meetings[self.next_meeting_id-1]}")

    @_meeting.subcommand(name="cancel", description="Cancel a meeting")
    async def _mt_cancel(self, interaction: Interaction, id: int):
        try:
            self.meetings[id].teardown()
            del self.meetings[id]
        except KeyError:
            await interaction.send("No such meeting.", ephemeral=True)
        else:
            await interaction.send(f"Meeting canceled!")

    @_meeting.subcommand(name="busy", description="Mark yourself as busy for a given time period")
    async def _mt_mark_busy(self, interaction: Interaction, start: str = timeopt, end: str = timeopt):
        if not isinstance(interaction.user, nextcord.Member):
            await interaction.send("Not sure what you are.", ephemeral=True)
            return
        st = parse_timeopt(start)
        en = parse_timeopt(end)
        if st is None or en is None:
            await interaction.send("Invalid format - see hint in description.", ephemeral=True)
            return
        if st >= en:
            await interaction.send("Start time must come before end time.", ephemeral=True)
            return
        newblock = TimeBlock(st, en)
        self._get_user(interaction.user).timeblocks.append(newblock)
        await interaction.send(f"You are now busy from {newblock}")

    @_meeting.subcommand(name="view", description="View info about a meeting")
    async def _mt_view(self, interaction: Interaction, id: int):
        try:
            await self._manage_meeting_embed(interaction, id, self.meetings[id])
        except KeyError:
            await interaction.send("No such meeting.", ephemeral=True)

    async def _manage_meeting_embed(self, interaction: Interaction, id: int, meeting: Meeting):
        button_timeout = 60
        buttons = ConfirmButtons(timeout=button_timeout)
        fields = [EmbedField(title=f"{e.user.display_name}", content="", inline=True) for e in meeting.users]
        emb = build_embed(*fields, title=f"Meeting {id}: {meeting}")
        await interaction.send(embed=emb, view=buttons)
        while not buttons.is_finished():
            await buttons.wait()
            if buttons.value == ButtonEnums.ACCEPT:
                meeting.register_user(self._get_user(buttons.user))
            elif buttons.value == ButtonEnums.DENY:
                meeting.deregister_user(self._get_user(buttons.user))
            fields = [EmbedField(title=f"{e.user}", content="", inline=True) for e in meeting.users]
            emb = build_embed(*fields, title=f"Meeting {id}: {meeting}")
            buttons = ConfirmButtons(timeout=button_timeout)
            await interaction.edit_original_message(embed=emb, view=buttons)
        await interaction.edit_original_message(embed=emb, view=None)
