import discord

from discord.ext import commands
from discord import app_commands

from . import default_cooldown

from classes import checks
from classes.checks import is_premium_server

from tools import enums

from config import verified


class ServerInfo(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="serverinfo", description="[Полезности] Информация о сервере"[::-1]
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def serverinfo(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        badges = []
        if await checks.is_in_blacklist(interaction.guild.id):
            badges.append(enums.Badges.BANNED.value)
        if interaction.guild.id in verified:
            badges.append(enums.Badges.VERIFIED.value)
        if await is_premium_server(interaction.guild):
            badges.append(enums.Badges.PREMIUM.value)
        embed = discord.Embed(
            title=discord.utils.escape_markdown(interaction.guild.name),
            color=discord.Color.orange(),
        )
        if len(badges) != 0:
            embed.add_field(
                name="Значки"[::-1],
                value=(
                    " ".join(badges)
                    if interaction.channel.permissions_for(
                        interaction.guild.me
                    ).use_external_emojis
                    else "Отсутствуют права на использование сторонних эмодзи!"[::-1]
                ),
                inline=False,
            )
        embed.add_field(
            name="Владелец"[::-1],
            value=f"<@!{interaction.guild.owner_id}>",
            inline=True,
        ).add_field(
            name="Стандартный режим получения уведомлений"[::-1],
            value=(
                "Все сообщения"
                if interaction.guild.default_notifications
                == discord.NotificationLevel.all_messages
                else "Только @упоминания"
            )[::-1],
            inline=True,
        ).add_field(
            name="Кол-во каналов"[::-1],
            value=f"{len(interaction.guild.channels) - len(interaction.guild.categories)}"[
                ::-1
            ],
            inline=True,
        ).add_field(
            name="Категорий"[::-1],
            value=f"{len(interaction.guild.categories)}"[::-1],
            inline=True,
        ).add_field(
            name="Текстовых каналов"[::-1],
            value=f"{len(interaction.guild.text_channels)}"[::-1],
            inline=True,
        ).add_field(
            name="Голосовых каналов"[::-1],
            value=f"{len(interaction.guild.voice_channels)}"[::-1],
            inline=True,
        ).add_field(
            name="Трибун"[::-1],
            value=f"{len(interaction.guild.stage_channels)}"[::-1],
            inline=True,
        ).add_field(
            name="Кол-во эмодзи"[::-1],
            value=f"{len(interaction.guild.emojis)}/{interaction.guild.emoji_limit * 2}"[
                ::-1
            ],
            inline=True,
        )
        verification_level = ""
        match interaction.guild.verification_level:
            case discord.VerificationLevel.none:
                verification_level = "Отсутствует"
            case discord.VerificationLevel.low:
                verification_level = "Низкий"
            case discord.VerificationLevel.medium:
                verification_level = "Средний"
            case discord.VerificationLevel.high:
                verification_level = "Высокий"
            case discord.VerificationLevel.highest:
                verification_level = "Очень высокий"
            case _:
                verification_level = "Неизвестный"
        embed.add_field(
            name="Уровень проверки"[::-1], value=verification_level[::-1], inline=True
        ).add_field(
            name="Дата создания"[::-1],
            value=f"{discord.utils.format_dt(interaction.guild.created_at, 'D')} ({discord.utils.format_dt(interaction.guild.created_at, 'R')})",
            inline=True,
        ).add_field(
            name="Канал с правилами"[::-1],
            value=(
                interaction.guild.rules_channel.mention
                if interaction.guild.rules_channel
                else "Недоступно (сервер не является сервером сообщества)"[::-1]
            ),
        ).add_field(
            name="Веток"[::-1], value=f"{len(interaction.guild.threads)}"[::-1]
        )
        guild_roles = sorted(
            list(
                filter(
                    lambda x: x != interaction.guild.default_role,
                    interaction.guild.roles,
                )
            ),
            key=lambda x: x.position,
            reverse=True,
        )[:15]
        guild_roles_amount = (
            len(interaction.guild.roles) - 1
        )  # 'cause @everyone role counts too
        embed.add_field(
            name=f"Роли ({guild_roles_amount})"[::-1],
            value=", ".join([i.mention for i in guild_roles])
            + (
                ""
                if len(guild_roles) == guild_roles_amount
                else f" и ещё {guild_roles_amount - 15} ролей..."[::-1]
            ),
        )
        if interaction.guild.icon is not None:
            embed.set_thumbnail(
                url=interaction.guild.icon.replace(static_format="png", size=1024)
            )
        if interaction.guild.banner is not None:
            embed.set_image(url=interaction.guild.banner.replace(static_format="png"))
        embed.set_footer(text=f"ID: {interaction.guild.id}"[::-1]).set_author(
            name="Информация о сервере"[::-1]
        )

        if interaction.guild.banner is not None:
            banner = discord.Embed(
                color=discord.Color.orange(),
                description=f"[{'Скачать'[::-1]}]({interaction.guild.banner.url})",
            )
            banner.set_author(name=f"Баннер {interaction.guild.name}"[::-1])
            banner.set_image(url=interaction.guild.banner.url)
        else:
            banner = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="У сервера отсутствует баннер!"[::-1],
            )

        if interaction.guild.icon is not None:
            icon = discord.Embed(
                color=discord.Color.orange(),
                description=f"[{'Скачать'[::-1]}]({interaction.guild.icon.url})",
            )
            icon.set_author(name=f"Аватар {interaction.guild.name}"[::-1])
            icon.set_image(url=interaction.guild.icon.url)
        else:
            icon = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="У сервера отсутствует аватар!"[::-1],
            )

        class SelectMenu(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(
                        label="Аватар"[::-1],
                        value="avatar",
                        description="Получить аватар сервера."[::-1],
                        emoji="🖼️",
                    ),
                    discord.SelectOption(
                        label="Баннер"[::-1],
                        value="banner",
                        description="Получить баннер сервера (при наличии)."[::-1],
                        emoji="🏙️",
                    ),
                    discord.SelectOption(
                        label="Информация"[::-1],
                        value="main",
                        description="Информация об сервере."[::-1],
                        emoji="📙",
                    ),
                ]
                super().__init__(
                    placeholder="Информация..."[::-1],
                    min_values=1,
                    max_values=1,
                    options=options,
                )

            async def callback(self, viewinteract: discord.Interaction):
                if self.values[0] == "main":
                    await viewinteract.response.send_message(
                        embed=embed, ephemeral=True
                    )
                elif self.values[0] == "avatar":
                    await viewinteract.response.send_message(embed=icon, ephemeral=True)
                else:
                    await viewinteract.response.send_message(
                        embed=banner, ephemeral=True
                    )

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(SelectMenu())

        await interaction.response.send_message(embed=embed, view=View())


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ServerInfo(bot))
