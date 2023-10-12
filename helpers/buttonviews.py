import resources.symbols as symbols
from enum import Enum
import nextcord


class ButtonEnums (Enum):
    LEFT = 0
    RIGHT = 1
    CLOSE = 2
    ACCEPT = 3
    DENY = 4


class PageButtons(nextcord.ui.View):
    '''
    Page buttons including left, right, and close
    '''

    def __init__(self, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.value: ButtonEnums = None
        self.user: nextcord.Member = None

    @nextcord.ui.button(label=symbols.LEFT_ARROW, style=nextcord.ButtonStyle.gray)
    async def left(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = ButtonEnums.LEFT
        self.user = interaction.user
        self.stop()

    @nextcord.ui.button(label=symbols.RIGHT_ARROW, style=nextcord.ButtonStyle.gray)
    async def right(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = ButtonEnums.RIGHT
        self.user = interaction.user
        self.stop()

    @nextcord.ui.button(label=symbols.X_SIGN, style=nextcord.ButtonStyle.red)
    async def close(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = ButtonEnums.CLOSE
        self.user = interaction.user
        self.stop()


class CloseButton(nextcord.ui.View):
    '''
    Single close button
    '''

    def __init__(self, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.value: ButtonEnums = None
        self.user: nextcord.Member = None

    @nextcord.ui.button(label=symbols.X_SIGN, style=nextcord.ButtonStyle.red)
    async def close(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = ButtonEnums.CLOSE
        self.user = interaction.user
        self.stop()


class ConfirmButtons(nextcord.ui.View):
    '''
    Accept and deny buttons
    '''

    def __init__(self, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.value: ButtonEnums = None
        self.user: nextcord.Member = None

    @nextcord.ui.button(label=symbols.CHECK_SIGN, style=nextcord.ButtonStyle.green)
    async def accept(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = ButtonEnums.ACCEPT
        self.user = interaction.user
        self.stop()

    @nextcord.ui.button(label=symbols.X_SIGN, style=nextcord.ButtonStyle.red)
    async def deny(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = ButtonEnums.DENY
        self.user = interaction.user
        self.stop()
