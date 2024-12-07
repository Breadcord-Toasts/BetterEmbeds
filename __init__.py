import discord
from discord.ext import commands

import breadcord
from breadcord.helpers import simple_button
from .constants import GITHUB_LINE_NUMBER_URL_REGEX, DISCORD_MESSAGE_URL_REGEX


class DeleteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @simple_button(label="Delete", style=discord.ButtonStyle.red, emoji="🗑️")
    async def delete(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        await interaction.message.delete()


class BetterEmbeds(breadcord.helpers.HTTPModuleCog):
    def __init__(self, module_id: str):
        super().__init__(module_id)
        self.bot.add_view(DeleteView())

    async def cog_load(self) -> None:
        await super().cog_load()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.content or message.author.bot:
            return

        def is_enabled(setting_key: str) -> bool:
            return self.settings.get(setting_key).value

        if is_enabled("github"):
            await self.handle_github_url(message)
        if is_enabled("message_links"):
            await self.handle_message_url(message)

    async def handle_github_url(self, message: discord.Message) -> None:
        for match in GITHUB_LINE_NUMBER_URL_REGEX.finditer(message.content):
            owner, repo, branch, file_path, file_ext, l1, l2 = match.groupdict().values()
            if not all((owner, repo, branch, file_path, l1)):
                continue

            start_i, end_i = match.span()
            is_spoiler: bool = (
                (message.content[start_i-2:start_i] == "||" and message.content[end_i:end_i+2] == "||")
                or (message.content[start_i-3:start_i] == "||<" and message.content[end_i:end_i+3] == ">||")
            )

            headers = {"Accept": "application/vnd.github.raw"}
            if github_token := self.settings.github_token.value:
                headers["Authorization"] = f"Bearer {github_token}"
            async with self.session.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}.{file_ext}?ref={branch}",
                headers=headers
            ) as response:
                if response.status != 200:
                    self.logger.warning(f"Could not fetch file {response.url}: {response.status}")
                    continue
                lines = (await response.text()).splitlines()

            l1 = int(l1) - 1
            l2 = (int(l2) - 1 if l2 else l1) + 1
            linked_lines = lines[l1:l2]
            indent = min(len(line) - len(line.lstrip()) for line in linked_lines if line.strip())
            code = "\n".join(line[indent:] for line in linked_lines)
            codeblock = f"```{file_ext or ''}\n{code}\n```"
            if is_spoiler:
                codeblock = f"||{codeblock}||"

            if not code or len(codeblock) > 2000:
                return
            view = DeleteView()
            await message.reply(
                codeblock,
                mention_author=False,
                view=view,
            )

    async def handle_message_url(self, message: discord.Message) -> None:
        for match in DISCORD_MESSAGE_URL_REGEX.finditer(message.content):
            guild_id, channel_id, message_id = match.groups()
            if not guild_id or not channel_id or not message_id:
                continue

            try:
                guild = self.bot.get_guild(int(guild_id))
                channel = guild.get_channel(int(channel_id))
                linked_message = await channel.fetch_message(int(message_id))
            except (AttributeError, discord.NotFound):
                self.logger.warning(f"Could not find message in {guild_id}/{channel_id}/{message_id}")
                continue

            view = DeleteView()
            await message.reply(
                embed=discord.Embed(
                    title=f"Message in {channel.mention}",
                    description=linked_message.content,
                    color=message.author.color,
                    timestamp=linked_message.created_at,
                ).set_author(
                    name=linked_message.author.display_name,
                    icon_url=linked_message.author.avatar.url if linked_message.author.avatar else None
                ),
                mention_author=False,
                view=view,
            )


async def setup(bot: breadcord.Bot, module: breadcord.module.Module) -> None:
    await bot.add_cog(BetterEmbeds(module.id))
