import discord
from discord.ext import commands

import breadcord
from breadcord.helpers import simple_button
from .constants import GITHUB_LINE_NUMBER_URL_REGEX


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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        def is_enabled(setting_key: str) -> bool:
            return self.settings.get(setting_key).value

        if is_enabled("github"):
            await self.handle_github_url(message)

    async def handle_github_url(self, message: discord.Message) -> None:
        if not message.content or message.author.bot:
            return
        for match in GITHUB_LINE_NUMBER_URL_REGEX.finditer(message.content):
            owner, repo, branch, file_path, file_ext, l1, l2 = match.groupdict().values()
            if not all((owner, repo, branch, file_path, l1)):
                continue

            headers = {"Accept": "application/vnd.github.raw"}
            if github_token := self.settings.github_token.value:
                headers["Authorization"] = f"Bearer {github_token}"
            async with self.session.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}.{file_ext}?ref={branch}",
                headers=headers
            ) as response:
                self.logger.debug(f"Fetching {response.url}")
                if response.status != 200:
                    continue
                lines = (await response.text()).splitlines()

            l1 = int(l1) - 1
            l2 = (int(l2) - 1 if l2 else l1) + 1
            linked_lines = lines[l1:l2]
            indent = min(len(line) - len(line.lstrip()) for line in linked_lines if line.strip())
            code = "\n".join(line[indent:] for line in linked_lines)
            codeblock = f"```{file_ext or ''}\n{code}\n```"

            if not code or len(codeblock) > 2000:
                return
            view = DeleteView()
            await message.reply(
                codeblock,
                mention_author=False,
                view=view,
            )


async def setup(bot: breadcord.Bot):
    await bot.add_cog(BetterEmbeds("better_embeds"))
