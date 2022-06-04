# -*- coding: utf-8 -*-
import discord, datetime, sys, typing, requests, config, boticordpy
from boticordpy import BoticordClient
from base64 import b64decode, b64encode
from asyncio import sleep, TimeoutError
from discord import NotFound, Forbidden, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from config import *

def is_shutted_down(interaction: discord.Interaction):
    return interaction.command.name not in shutted_down

def cooldown_check(interaction: discord.Interaction):
    return None if interaction.user.id == settings['owner_id'] else app_commands.Cooldown(1, 300)

class Tools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.boticord_client = BoticordClient(settings['boticord_key'])

        @app_commands.check(is_shutted_down)
        class base64(app_commands.Group):
            """[Полезности] (Де-)кодирует указанный текст в Base64."""

            @app_commands.command(description="[Полезности] Кодирует указанный текст в Base64.")
            @app_commands.check(is_shutted_down)
            @app_commands.describe(text="Текст для кодировки")
            async def encode(self, interaction: discord.Interaction, text: str):
                config.used_commands += 1
                if interaction.user.id in blacklist:
                    embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
                    embed.set_thumbnail(url=interaction.user.avatar.url)
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                config.lastcommand = '`/base64 encode`'
                text = text[:1020] + (text[1020:] and '..')
                ans = text.encode("utf8")
                ans = b64encode(ans)
                ans = str(ans).removeprefix("b'")
                ans = str(ans).removesuffix("'")
                if len(text) > 1024 or len(ans) > 1024:
                    embed = discord.Embed(title="Зашифровка:", color=discord.Color.orange(), description=f"**Исходный текст:**\n{text}")
                    embed1 = discord.Embed(title="Полученный текст:", color=discord.Color.orange(), description=ans)
                    return await interaction.response.send_message(embeds=[embed, embed1], ephemeral=True)
                embed = discord.Embed(title="Зашифровка:", color=discord.Color.orange())
                embed.add_field(name="Исходный текст:", value=text, inline=False)
                embed.add_field(name="Полученный текст:", value=ans)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            @app_commands.command(description="[Полезности] Декодирует Base64 в текст.")
            @app_commands.check(is_shutted_down)
            @app_commands.describe(text="Текст для декодировки")
            async def decode(self, interaction: discord.Interaction, text: str):
                config.used_commands += 1
                if interaction.user.id in blacklist:
                    embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
                    embed.set_thumbnail(url=interaction.user.avatar.url)
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                config.lastcommand = '`/base64 decode`'
                try:
                    ans = b64decode(text)
                    ans = ans.decode("utf8")
                except:
                    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Невозможно расшифровать строку!")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                if len(text) > 1024 or len(ans) > 1024:
                    embed = discord.Embed(title="Зашифровка:", color=discord.Color.orange(), description=f"**Исходный текст:**\n{text}")
                    embed1 = discord.Embed(title="Полученный текст:", color=discord.Color.orange(), description=ans)
                    return await interaction.response.send_message(embeds=[embed, embed1], ephemeral=True)
                embed = discord.Embed(title="Расшифровка:", color=discord.Color.orange())
                embed.add_field(name="Исходный текст:", value=text, inline=False)
                embed.add_field(name="Полученный текст:", value=ans)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        self.bot.tree.add_command(base64())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or message.author.id in blacklist:
            return

        if message.channel.id == settings['github_channel']:
            await sleep(10) # Задержка, чтобы можно было успеть удалить сообщение.
            try:
                await message.publish()
            except:
                pass

        if message.content.startswith('Дарова, ботяра'):
            await message.reply(f' {message.author.mention} бот, не я')

        if message.content.startswith("/"):
            embed = discord.Embed(title="Команда введена неправильно!", color=discord.Color.red(), description="У бота `/` является не префиксом, а вызовом слеш-команд. Полностью очистите строку сообщений, поставьте `/` и выберите команду из списка.")
            await message.reply(embed=embed, delete_after=20)
        
        if message.author.id == 963819843142946846: # Триггер на сообщения мониторинга.
            await sleep(3)
            if message.content == "mad.debug ping":
                await message.channel.send(int(round(self.bot.latency, 3)*1000))
            if message.content == "mad.debug status":
                await message.channel.send("OK")

        if message.content.startswith((f"<@!{self.bot.user.id}>") or message.content.startswith(f"<@{self.bot.user.id}>") and message.content.find("debug") == -1):
            embed=discord.Embed(title="Привет! Рад, что я тебе чем-то нужен!", color=discord.Color.orange(), description="Бот работает на слеш-командах, поэтому для взаимодействия с ботом следует использовать их. Для большей информации пропишите `/help`.")
            await message.reply(embed=embed, mention_author=False)
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data['component_type'] == 2:
            try:
                role_id = int(interaction.data['custom_id'])
            except:
                pass
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
                role = interaction.guild.get_role(role_id)
                if role == None:
                    return
                if role_id in [role.id for role in member.roles]:
                    try:
                        await member.remove_roles(role, reason="Нажатие на кнопку")
                    except:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Бот не имеет права `управлять ролями`, что необходимо для работы функции!"
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    embed = discord.Embed(
                        title="Выбор роли", 
                        color=discord.Color.green(),
                        description=f"Роль {role.mention} успешно убрана!"
                    )
                else:
                    try:
                        await member.add_roles(role, reason="Нажатие на кнопку")
                    except:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Бот не имеет права `управлять ролями`, что необходимо для работы функции!"
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    embed = discord.Embed(
                        title="Выбор роли", 
                        color=discord.Color.green(),
                        description=f"Роль {role.mention} успешно добавлена!"
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                pass

    @app_commands.command(description="[Полезности] Показывает изменения в текущей версии.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(ver="Версия бота")
    @app_commands.choices(ver=[
        Choice(name="Актуальная", value="actual"),
        Choice(name="0.10", value='010'),
        Choice(name="0.9", value="09"),
        Choice(name="0.8", value="08"),
        Choice(name="0.7", value='07'),
        Choice(name="0.6", value='06'),
        Choice(name="0.5", value="05"),
        Choice(name="0.4", value="04"),
        Choice(name="0.3.9", value="039"),
        Choice(name="0.3.8", value="038"),
        Choice(name="0.3.7", value="037"),
        Choice(name="0.3.6", value="036")
    ])
    async def version(self, interaction: discord.Interaction, ver: Choice[str] = None):
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/version`"
        embed = None
        if ver != None:
            ver = ver.name
        if ver == None or ver == '0.10' or ver == "Актуальная":
            updated_at = datetime.datetime(2022, 5, 31, 17, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.10`', color=discord.Color.orange(), timestamp=updated_at, description=f"> 1) Добавление `/russian-roulette` и `/duel`.\n> 2) Использование кнопок-ссылок в `/botinfo`.\n> 3) Добавлена страница бота на Boticord в `/botinfo`.\n> 4) Добавлено угадывание числа (`/number`).\n> 5) Улучшение статистики `/botinfo`.\n> 6) При ошибке, кнопки сообщения будут убраны.\n> 7) Предосторожности в `/weather`.\n> 8) Добавлена команда `/autorole` для настройки ролей на нажатие кнопок.\n> 9) Добавлена команда `/dice`.\n> 10) Изменение сообщения о кулдауне.")
            embed.set_footer(text="Обновлено:")
        if ver == '0.9':
            updated_at = datetime.datetime(2022, 5, 25, 21, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.9`', color=discord.Color.orange(), timestamp=updated_at, description=f"> 1) Исправление бага со счётом команд в `/botinfo`.\n> 2) Добавлены полезная команда `/stopwatch`.\n> 3) Добавлена развлекательная команда `/knb`, `/coin`.\n> 4) Команда `/base64` теперь - группа.\n> 5) Добавлена команда `/debug` для получения сведений о боте.\n> 6) Команда `/idea` теперь в кулдауне (раз в 5 минут).\n> 7) Учет embed'ов и файлов в док-вах в контекстных меню.\n> 8) Добавлена обратная связь через `/help`. ~~Конец `/idea`?~~\n> 9) Новый значок - помощник разработчика.\n> 10) Добавлена игра `/tic-tac-toe`. Спасибо, F_Artamon#7588.\n> 11) Добавлена игра `/hangman`.")
            embed.set_footer(text="Обновлено:")
        if ver == '0.8':
            updated_at = datetime.datetime(2022, 5, 17, 20, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.8`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Требование права на просмотр журнала аудита в `/getaudit`.\n> 2) Показ кол-во участников в сети в `/serverinfo`.\n> 3) Изменение вида `/serverinfo`.\n> 4) Добавление Select Menu в `/userinfo` и `/serverinfo`.\n> 5) Команды могут быть отключены владельцем бота.\n> 6) Добавлено новое развлечение: `/doors`.\n> 7) Использование кнопок и форм вместо реакций и сообщений.\n> 8) Добавлена команда `/weather`.\n> 9) Иногда, бот будет показывать свою версию в статусе.\n> 10) Добавлена команда `/ball`.\n> 11) Обновлен дизайн `/botinfo` и `/help`.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.7':
            updated_at = datetime.datetime(2022, 5, 8, 20, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.7`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Исправлена команда `/base64`.\n> 2) Обновлен дизайн `/botinfo` и `/avatar`.\n> 3) Запрос на смену ника при отсутствии права на изменение никнейма в `/nick`.\n> 4) Небольшое дополнение команды `/nsfw`.\n> 5) Авто-постинг новостей из <#953175109135376394>.\n> 6) Показ типа операционной системы, на которой запущен бот, в `/botinfo`.\n> 7) Показ списка ролей сервера в `/serverinfo`.\n> 8) Теперь приветственное сообщение будет присылаться в ЛС добавившему бота, если это возможно.\n> 9) Команда `/outages` снова работает.\n> 10) При правильном ответе, бот пишет время ответа в `/math`.\n> 11) Добавлена команда `/clearoff`.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.6':
            updated_at = datetime.datetime(2022, 5, 5, 20, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.6`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Исправление обхода проверки иерархии, используя `/banoff`.\n> 2) Добавлены контекстные меню модерации.\n> 3) Добавлены команды `/kiss` и `/hit`.\n> 4) Для поцелуя необходимо получить разрешение от второго участника.\n> 5) Добавлена первая развлекательная команда: `/math`.\n> 6) Улучшение системы мониторинга бота.\n> 7) Поддержка ввода эмодзи в `/getemoji`.\n> 8) Фильтрация гифок в `/slap`. Не хочу случайно получить бан.\n> 9) Коллаборация `/clear` и `/clearfrom`.\n> 10) Добавлен счетчик обработанных команд в `/botinfo`.\n> 11) В заголовке `/serverinfo` отображается количество ботов.\n> 12) Куча исправлений.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.5':
            updated_at = datetime.datetime(2022, 4, 18, 19, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.5`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Добавлена команда `/banoff`.\n> 2) Добавлены команды реакций.\n> 3) Добавлены контекстные меню. Со временем их будет больше.\n> 4) Бот оповещает участника о выдаче участнику наказания.\n> 5) Добавлена команда `/getemoji`.\n> 6) Добавлены команды `/dog` и `/cat`.\n> 7) В `/botinfo` появился показ версий Python и discord.py, а так же показ кол-ва обработанных команд.\n> 8) Добавлена команда `/nsfw`. Применение объяснять не надо (так ведь?).\n> 9) В тестовом режиме добавлена команда `/base64`. Шифрует она только латиницу.\n> 10) Теперь в `/clearfrom` можно очищать сообщения любых участников.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.4':
            updated_at = datetime.datetime(2022, 3, 27, 19, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.4 [ОБТ]`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Исправлена команда `/serverinfo`.\n> 2) Добавлено поле "Запущено" в `/botinfo`.\n> 3) Добавлено поле "Статус" в `/userinfo`.\n> 4) Исправлена возможность выдать наказание участнику, чья роль выше либо равна роли модератора.\n> 5) Теперь надо выбирать размер аватара вместо ручного ввода в команде `/avatar`.\n> 6) Обновлена ссылка на поддержку бота в его "обо мне".\n> 7) Добавлены значки "Bug Hunter" и "Bug Terminator". Подробнее: `/badgeinfo`.\n> 8) Теперь нельзя сбрасывать ник ботам. Не спрашивайте, почему.\n> 9) Теперь пинг (который без лишнего нуля) виден в статусе бота.\n> 10) Уточнение в `/clearfrom`.\n> 11) Добавлена команда `/unban` (спустя полгода с добавления команды `/ban`).\n> 12) Добавлена команда `/idea` для публикации идей в канал <#957688771200053379>.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.3.9':
            updated_at = datetime.datetime(2022, 3, 17, 19, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.3.9 [ОБТ]`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Добавлены команды `/resetnick`, `/clone` и `/nick`.\n> 2) Команда `/cooldown` переименована в `/slowmode`.\n> 3) Для команд модерации добавлено обязательное указание причины.\n> 4) При ошибках в командах модерации показывается тип ошибки.\n> 5) Добавлена команда `/errors` для самостоятельного решения ошибок.\n> 6) Немного изменено оформление "обо мне" бота.\n> 7) Ошибки будут логироваться в канале логов бота на сервере поддержки. Это сделано для быстрого обнаружения проблемы и исправления её.\n> 8) При использовании команды `/nick` и отсутствии прав на изменение ника, бот запросит подтверждение изменения ника у администраторов.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.3.8':
            updated_at = datetime.datetime(2022, 3, 7, 19, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.3.8 [ОБТ]`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Переезд на `discord.py v2.0`.\n> 2) Исправлена проблема с вводом причины в `/timeout`.\n> 3) Удалена команда `/beauty`.\n> 4) Исправлена возможность ввести значение ниже `1` в `/clear` и `/clearfrom`.\n> 5) Возможность посмотреть изменения в предыдущих версиях в `/version`.\n> 6) Теперь в `/userinfo` показывается по умолчанию серверная аватарка (если есть).\n> 7) При наличии **стандартного** баннера, он будет виден в `/userinfo`.\n> 8) Можно выбрать тип аватара (серверный либо стандартный) в `/avatar`.')
            embed.set_footer(text="Обновлено:")
        if ver == "0.3.7":
            updated_at = datetime.datetime(2022, 3, 4, 18, 0, 0, 0)
            embed=discord.Embed(title="Версия `0.3.7 [ОБТ]`", color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Добавлены значки в `/userinfo` и `/serverinfo`.\n> 2) Добавлена команда `/badgeinfo` для ознакомления со значками.\n> 3) Исправлен баг с неактуальной ссылкой на поддержку в `/botinfo`.\n> 4) Добавлена возможность просмотра последней использованной команды бота в `/botinfo`.\n> 5) Пользователи теперь могут попасть в чёрный список бота.\n> 6) [BETA] Появилась возможность проверить, находится ли участник в чёрном списке бота.\n> 7) Можно узнать о боте, упомянув его.\n> 8) В случае, если вы будете использовать `/` как префикс бота, он вам сделает предупреждение.\n> 9) Добавлена команда `/help` для первичного ознакомления с ботом.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.3.6':
            updated_at = datetime.datetime(2022, 2, 17, 9, 0, 0, 0)
            embed=discord.Embed(title="Версия `0.3.6 [ОБТ]`", color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Добавлены таймштампы в `/serverinfo` и `/userinfo`.\n> 2) Добавлено поле "Присоединился" в `/userinfo`.\n> 3) Теперь видно, когда бот перезапускается в его статусе.\n> 4) Изменена аватарка.\n> 5) Изменен порядок аргументов по умолчанию в `/clearfrom`.\n> 6) Добавлена "Защита от дурака" в `/avatar` при вводе параметра `size`.\n> 7) Добавлено поле "Кол-во участников" в `/botinfo`.')
            embed.set_footer(text="Обновлено:")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="errors", description="[Полезности] Список ошибок и решения их")
    @app_commands.check(is_shutted_down)
    async def errors(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/errors`"
        embed = discord.Embed(title="Ошибки бота:", color=discord.Color.orange())
        embed.add_field(name="Ошибка: Forbidden", value="Бот не может совершить действие. Убедитесь, что бот имеет право(-а) на совершение действия.", inline=False)
        embed.add_field(name="Ошибка: NotFound", value="Боту не удалось найти объект (пользователя, сервер и т.д.).", inline=False)
        embed.add_field(name="Ошибка: HTTPException", value="Бот отправил некорректный запрос на сервера Discord, из-за чего получил ошибку. Убедитесь, что вы ввели всё верно.", inline=False)
        embed.set_footer(text="В случае, если вашей ошибки нет в списке, обратитесь в поддержку.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="[Полезности] Показывает основную информацию о боте.")
    @app_commands.check(is_shutted_down)
    async def help(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/help`"
        commands = self.bot.tree.get_commands(type=discord.AppCommandType.chat_input)
        mod_commands = ""
        tools_commands = ""
        ent_commands = ""
        for command in commands:
            if command.description.startswith("[Модерация]"):
                mod_commands += f"`/{command.name}` - {command.description.removeprefix('[Модерация]')}\n"
            if command.description.startswith("[Полезности]"):
                tools_commands += f"`/{command.name}` - {command.description.removeprefix('[Полезности]')}\n"
            if command.description.startswith("[Развлечения]") or command.description.startswith("[NSFW]") or command.description.startswith("[Реакции]"):
                ent_commands += f"`/{command.name}` - {command.description.removeprefix('[Развлечения]').removeprefix('[NSFW]').removeprefix('[Реакции]')}\n"

        moderation = discord.Embed(
            title=f"{self.bot.user.name} - Модерация", 
            color=discord.Color.orange(), 
            description=mod_commands
        )
        tools = discord.Embed(
            title=f"{self.bot.user.name} - Полезности",
            color=discord.Color.orange(), 
            description=tools_commands
        )
        entartaiment = discord.Embed(
            title=f"{self.bot.user.name} - Развлечения",
            color=discord.Color.orange(), 
            description=ent_commands
        )
        embed = discord.Embed(title=f"{self.bot.user.name} - Главная", color=discord.Color.orange(), description=f"Спасибо за использование {self.bot.user.name}! Я использую слеш-команды, поэтому для настройки доступа к ним можно использовать настройки Discord.")
        embed.add_field(name="Поддержка:", value=settings['support_invite'], inline=False)
        embed.add_field(name="Пригласить:", value=f"[Тык](https://discord.com/oauth2/authorize?client_id={settings['app_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands)", inline=False)
            
        class DropDownCommands(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Главная", value="embed", description="Главное меню.", emoji="🐱"),
                    discord.SelectOption(label="Модерация", value="moderation", description="Команды модерации.", emoji="🛑"),
                    discord.SelectOption(label="Полезности", value="tools", description="Полезные команды.", emoji="⚒️"),
                    discord.SelectOption(label="Развлечения", value="entartaiment", description="Развлекательные команды.", emoji="🎉")
                ]
                super().__init__(placeholder="Команды", options=options)
            
            async def callback(self, viewinteract: discord.Interaction):
                if interaction.user.id != viewinteract.user.id:
                    if self.values[0] == "embed":
                        return await viewinteract.response.send_message(embed=embed, ephemeral=True)
                    elif self.values[0] == "moderation":
                        return await viewinteract.response.send_message(embed=moderation, ephemeral=True)
                    elif self.values[0] == "tools":
                        return await viewinteract.response.send_message(embed=tools, ephemeral=True)
                    else:
                        return await viewinteract.response.send_message(embed=entartaiment, ephemeral=True)
                if self.values[0] == "embed":
                    await interaction.edit_original_message(embed=embed)
                elif self.values[0] == "moderation":
                    await interaction.edit_original_message(embed=moderation)
                elif self.values[0] == "tools":
                    await interaction.edit_original_message(embed=tools)
                else:
                    await interaction.edit_original_message(embed=entartaiment)
                await viewinteract.response.defer()

        class DropDownHelp(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Я нашел баг!", value="bugreport", description="Заполните форму, и мы исправим баг как можно скорее!", emoji='🐞'),
                    discord.SelectOption(label="У меня вопрос!", value="question", description="Заполните форму, и вам ответят на вопрос!", emoji='❓'),
                    discord.SelectOption(label="У меня идея!", value='idea', description="Заполните форму, и ваша идея будет рассмотрена!", emoji="💡")
                ]
                super().__init__(placeholder='Обратная связь', options=options)

            class BugReport(discord.ui.Modal, title="Сообщить о баге"):
                main = discord.ui.TextInput(label="Тема:", placeholder="Команда /команда выдаёт ошибку.", max_length=50)
                description = discord.ui.TextInput(label="Подробности:", placeholder="При таком-то действии бот выдает ошибку, хотя должен был сделать совсем другое.", style=discord.TextStyle.paragraph, max_length=2048)
                links = discord.ui.TextInput(label="Ссылки на док-ва:", required=False, style=discord.TextStyle.paragraph, max_length=1024, placeholder="https://imgur.com/RiCkROLl")

                async def on_submit(self, viewinteract: discord.Interaction):
                    log_channel = viewinteract.client.get_channel(settings['report_channel'])
                    embed = discord.Embed(title=f"Сообщение о баге: {str(self.main)}", color=discord.Color.red(), description=str(self.description))
                    embed.set_author(name=str(viewinteract.user), icon_url=viewinteract.user.display_avatar.url)
                    if str(self.links) != "":
                        embed.add_field(name="Ссылки:", value=str(self.links))
                    await log_channel.send(embed=embed)
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Сообщение о баге успешно отправлено!")
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                
            class AskQuestion(discord.ui.Modal, title="Задать вопрос"):
                main = discord.ui.TextInput(label="Тема:", placeholder="Как сделать так-то.", max_length=50)
                description = discord.ui.TextInput(label="Подробности:", placeholder="Я хочу сделать так. Как так сделать?", style=discord.TextStyle.paragraph, max_length=2048)
                links = discord.ui.TextInput(label="Ссылки на док-ва:", required=False, style=discord.TextStyle.paragraph, max_length=1024, placeholder="https://imgur.com/RiCkROLl")

                async def on_submit(self, viewinteract: discord.Interaction):
                    class Buttons(discord.ui.View):
                        def __init__(self, main: str):
                            super().__init__(timeout=None)
                            self.main = main
                        
                        @discord.ui.button(label="Ответить", style=discord.ButtonStyle.primary, emoji="✏️")
                        async def answer(self, buttinteract: discord.Interaction, button: discord.ui.Button):
                            if not (buttinteract.user.id in supports):
                                return await buttinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True) 
                            class AnswerQuestion(discord.ui.Modal, title="Ответ на вопрос"):
                                def __init__(self, main: str):
                                    super().__init__(custom_id="MadBotAnswerQuestion")
                                    self.main = main
                                answer = discord.ui.TextInput(label="Ответ:", placeholder="Сделайте вот так:", style=discord.TextStyle.paragraph, max_length=2048)

                                async def on_submit(self, ansinteract: discord.Interaction):
                                    embed = discord.Embed(title=f'Ответ на вопрос "{self.main}"!', color=discord.Color.green(), description=str(self.answer))
                                    embed.set_author(name=str(ansinteract.user), icon_url=ansinteract.user.display_avatar.url)
                                    try:
                                        await viewinteract.user.send(embed=embed)
                                    except:
                                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Бот не смог отправить ответ на вопрос в личные сообщения пользователя!")
                                        await ansinteract.response.send_message(embed=embed, ephemeral=True)
                                    else:
                                        embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Ответ отправлен пользователю.")
                                        await ansinteract.response.send_message(embed=embed, ephemeral=True)
                                    await buttinteract.edit_original_message(view=None)
                                
                            await buttinteract.response.send_modal(AnswerQuestion(self.main))

                    log_channel = viewinteract.client.get_channel(settings['report_channel'])
                    embed = discord.Embed(title=f"Вопрос: {str(self.main)}", color=discord.Color.red(), description=str(self.description))
                    embed.set_author(name=str(viewinteract.user), icon_url=viewinteract.user.display_avatar.url)
                    if str(self.links) != "":
                        embed.add_field(name="Ссылки:", value=str(self.links))
                    await log_channel.send(embed=embed, view=Buttons(self.main))
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Вопрос успешно отправлен!")
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                
            class SendIdea(discord.ui.Modal, title="Предложить идею"):
                main = discord.ui.TextInput(label='Суть идеи:', max_length=50, placeholder="Удалить конфликты.")
                description = discord.ui.TextInput(label="Идея:", max_length=2048, placeholder="Сделать так, чтобы везде был мир.", style=discord.TextStyle.long)
                links = discord.ui.TextInput(label="Ссылки:", max_length=1024, placeholder="https://imgur.com/RiCkROLl", required=False)

                async def on_submit(self, viewinteract: discord.Interaction):
                    idea_embed = discord.Embed(title=str(self.main), color=discord.Color.orange(), description=str(self.description), timestamp=discord.utils.utcnow())
                    idea_embed.set_author(name=viewinteract.user, icon_url=viewinteract.user.display_avatar)
                    if str(self.links) != '':
                        idea_embed.add_field(name="Ссылки:", value=str(self.links))
                    channel = viewinteract.client.get_channel(settings['idea_channel'])
                    message = await channel.send(embed=idea_embed)
                    await message.add_reaction("✅")
                    await message.add_reaction("💤")
                    await message.add_reaction("❌")
                    embed = discord.Embed(title='Успешно!', color=discord.Color.green(), description="Идея отправлена в канал")
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)

            async def callback(self, viewinteract: discord.Interaction):
                if viewinteract.user.id in blacklist:
                    embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
                    embed.set_thumbnail(url=interaction.user.avatar.url)
                    return await viewinteract.response.send_message(embed=embed, ephemeral=True)
                modals = {
                    'bugreport': self.BugReport(),
                    'question': self.AskQuestion(),
                    'idea': self.SendIdea()
                }
                await viewinteract.response.send_modal(modals[self.values[0]])
           
        class DropDownView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(DropDownCommands())
                self.add_item(DropDownHelp())

        await interaction.response.send_message(embed=embed, view=DropDownView())

    @app_commands.command(name="ping", description="[Полезности] Проверка бота на работоспособность")
    @app_commands.check(is_shutted_down)
    async def ping(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/ping`"
        embed = discord.Embed(color=discord.Color.dark_red(), title=self.bot.user.name, description=f'⚠ **ПОНГ!!!**\n⏳ Задержка: `{int(round(self.bot.latency, 3)*1000)}ms`.')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="[Полезности] Показывает информацию о пользователе")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member='Участник')
    async def userinfo(self, interaction: discord.Interaction, member: discord.User = None):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(member, discord.User):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Пользователь должен находиться на сервере для использования команды на нём!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        config.lastcommand = "`/userinfo`"
        global emb
        badges = ''
        guild = self.bot.get_guild(interaction.guild.id)
        if member == None:
            member = interaction.user
        else:
            try:
                member = await interaction.guild.fetch_member(member.id)
            except:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Участник должен находиться на сервере для использования команды!")
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        for memb in interaction.guild.members:
            if memb == member:
                member = memb
                break
        
        embed = discord.Embed(color=member.color, description=f"[Скачать]({member.display_avatar.replace(static_format='png', size=2048)})")
        embed.set_author(name=f"Аватар {member}")
        embed.set_image(url=member.display_avatar.replace(static_format="png", size=2048))
        embed.set_footer(text=f"Формат: png | Размер: 2048 | Тип аватара: Серверный.")

        member_color = member.color
        if member.id in blacklist:
            badges += '<:ban:946031802634612826> '
        if member.is_timed_out():
            badges += '<:timeout:950702768782458893> '
        if member.id == settings['owner_id']:
            badges += '<:botdev:977645046188871751> '
        if member.id in coders:
            badges += '<:code:946056751646638180> '
        if member.id in supports:
            badges += '<:support:946058006641143858> '
        if member.id in bug_hunters:
            badges += '<:bug_hunter:955497457020715038> '
        if member.id in bug_terminators:
            badges += '<:bug_terminator:955891723152801833> '
        if member.id in verified:
            badges += '<:verified:946057332389978152> '
        if member.bot:
            badges += '<:bot:946064625525465118> '
        member = guild.get_member(member.id)
        if member.nick == None:
            emb = discord.Embed(title=f"`{member.name}#{member.discriminator}` {badges}", color=member.color)
        else:
            emb = discord.Embed(title=f"`{member.name}#{member.discriminator}` | `{member.nick}` {badges}", color=member.color)
        emb.add_field(name="Упоминание:", value=member.mention, inline=False)
        if member.status == discord.Status.online:
            emb.add_field(name="Статус:", value="🟢 В сети", inline=False)
        elif member.status == discord.Status.idle:
            emb.add_field(name="Статус:", value="🌙 Нет на месте", inline=False)
        elif member.status == discord.Status.dnd:
            emb.add_field(name="Статус:", value="🔴 Не беспокоить", inline=False)
        else:
            emb.add_field(name="Статус:", value="🔘 Не в сети", inline=False)
        emb.add_field(name="Ссылка на профиль:", value=f"[Тык](https://discord.com/users/{member.id})", inline=False)
        if member.bot:
            emb.add_field(name="Бот?:", value="Да", inline=False)
        else:
            emb.add_field(name="Бот?:", value="Нет", inline=False)
        if member.guild_permissions.administrator:
            emb.add_field(name="Администратор?:", value=f'Да', inline=False)
        else:
            emb.add_field(name="Администратор?:", value='Нет', inline=False)
        emb.add_field(name="Самая высокая роль на сервере:", value=f"{member.top_role.mention}", inline=False)
        emb.add_field(name="Акаунт был создан:", value=f"{discord.utils.format_dt(member.created_at, 'D')} ({discord.utils.format_dt(member.created_at, 'R')})", inline=False)
        emb.add_field(name="Присоединился:", value=f"{discord.utils.format_dt(member.joined_at, 'D')} ({discord.utils.format_dt(member.joined_at, 'R')})", inline=False)
        emb.set_thumbnail(url=member.display_avatar.replace(static_format="png", size=1024))
        member = await self.bot.fetch_user(member.id)
        if member.banner != None:
            emb.set_image(url=member.banner.url)
        emb.set_footer(text=f'ID: {member.id}')

        if member.banner != None:
            banner = discord.Embed(color=member_color, description=f"[Скачать]({member.banner.url})")
            banner.set_author(name=f"Баннер {member}")
            banner.set_image(url=member.banner.url)
        else:
            banner = discord.Embed(title="Ошибка", color=discord.Color.red(), description="У пользователя отсутствует баннер!")

        class SelectMenu(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Аватар", value="avatar", description="Получить аватар пользователя.", emoji="🖼️"),
                    discord.SelectOption(label="Баннер", value="banner", description="Получить баннер пользователя (при наличии).", emoji="🏙️"),
                    discord.SelectOption(label="Информация", value="main", description="Информация об пользователе.", emoji="📙")
                ]
                super().__init__(placeholder="Информация...", min_values=1, max_values=1, options=options)
            
            async def callback(self, viewinteract: discord.Interaction):
                if self.values[0] == "main":
                    await viewinteract.response.send_message(embed=emb, ephemeral=True)
                elif self.values[0] == "avatar":
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                else:
                    await viewinteract.response.send_message(embed=banner, ephemeral=True)

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(SelectMenu())

        await interaction.response.send_message(embed=emb, view=View())

    @app_commands.command(name="avatar", description="[Полезности] Присылает аватар пользователя")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member='Участник, чью аватарку вы хотите получить', format="Формат изображения", size="Размер изображения", type="Тип аватара")
    @app_commands.choices(
        format=[
            Choice(name="PNG (прозрачный фон)", value="png"),
            Choice(name="JPEG (черный фон)", value="jpeg"),
            Choice(name="JPG (как JPEG)", value='jpg'),
            Choice(name="WEBP (веб-картинка)", value='webp')
        ],
        size=[
            Choice(name="16x16 пикселей", value=16),
            Choice(name="32x32 пикселей", value=32),
            Choice(name="64x64 пикселей", value=64),
            Choice(name="128x128 пикселей", value=128),
            Choice(name="256x256 пикселей", value=256),
            Choice(name="512x512 пикселей", value=512),
            Choice(name="1024x1024 пикселей", value=1024),
            Choice(name="2048x2048 пикселей", value=2048),
            Choice(name="4096x4096 пикселей", value=4096)
        ],
        type=[
            Choice(name="Стандартная", value='standart'),
            Choice(name="Серверная", value='server')
        ]
    )
    async def avatar(self, interaction: discord.Interaction, member: discord.User = None, format: Choice[str] = "png", size: Choice[int] = 2048, type: Choice[str] = 'server'):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/avatar`"
        if member == None:
            member = interaction.user
        if format != 'png':
            format = format.value
        if size != 2048:
            size = size.value
        if type != 'server':
            type = type.value
        user_avatar = member.display_avatar
        if member.avatar != None:
            user_avatar = member.avatar
        embed = discord.Embed(color=member.color, description=f"[Скачать]({user_avatar.replace(static_format=format, size=size)})")
        embed.set_author(name=f"Аватар {member}")
        embed.set_image(url=user_avatar.replace(static_format=format, size=size))
        if type == "server":
            type = "Серверный"
        else:
            type = "Стандартный"
        embed.set_footer(text=f"Запросил: {interaction.user.name}#{interaction.user.discriminator} | Формат: {format} | Размер: {size} | Тип аватара: {type}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="[Полезности] Информация о сервере")
    @app_commands.check(is_shutted_down)
    async def serverinfo(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/serverinfo`"
        badges = ''
        if interaction.guild.id in blacklist:
            badges += '<:ban:946031802634612826> '
        if interaction.guild.id in verified:
            badges += '<:verified:946057332389978152> '
        if interaction.guild.id in beta_testers:
            badges += '<:beta:946063731819937812> '
        bots = 0
        for member in interaction.guild.members:
            if member.bot:
                bots += 1
        online = len(list(filter(lambda x: x.status == discord.Status.online, interaction.guild.members)))
        idle = len(list(filter(lambda x: x.status == discord.Status.idle, interaction.guild.members)))
        dnd = len(list(filter(lambda x: x.status == discord.Status.dnd, interaction.guild.members)))
        offline = len(list(filter(lambda x: x.status == discord.Status.offline, interaction.guild.members)))
        embed = discord.Embed(title=f"{interaction.guild.name} {badges}", color=discord.Color.orange(), description=f"🟢 `{online}` | 🌙 `{idle}` | 🔴 `{dnd}` | ⚪ `{offline}`")
        embed.add_field(name="Владелец:", value=interaction.guild.owner.mention, inline=True)
        if interaction.guild.default_notifications == "all_messages":
            embed.add_field(name="Стандартный режим получения уведомлений:", value="Все сообщения", inline=True)
        else:
            embed.add_field(name="Стандартный режим получения уведомлений:", value="Только @упоминания", inline=True)
        embed.add_field(name="Кол-во каналов:", value=len(interaction.guild.channels) - len(interaction.guild.categories), inline=True)
        embed.add_field(name="Кол-во категорий:", value=len(interaction.guild.categories), inline=True)
        embed.add_field(name="Текстовых каналов:", value=len(interaction.guild.text_channels), inline=True)
        embed.add_field(name="Голосовых каналов:", value=len(interaction.guild.voice_channels), inline=True)
        embed.add_field(name="Трибун:", value=len(interaction.guild.stage_channels), inline=True)
        embed.add_field(name="Участники:", value=f"**Всего:** {interaction.guild.member_count}.\n**Участники:** {interaction.guild.member_count - bots}.\n**Боты:** {bots}.", inline=True)
        embed.add_field(name="Кол-во эмодзи:", value=f"{len(interaction.guild.emojis)}/{interaction.guild.emoji_limit * 2}", inline=True)
        temp = interaction.guild.verification_level
        if temp == discord.VerificationLevel.none:
            embed.add_field(name="Уровень проверки:", value="Отсутствует", inline=True)
        elif temp == discord.VerificationLevel.low:
            embed.add_field(name="Уровень проверки:", value="Низкий", inline=True)
        elif temp == discord.VerificationLevel.medium:
            embed.add_field(name="Уровень проверки:", value="Средний", inline=True)
        elif temp == discord.VerificationLevel.high:
            embed.add_field(name="Уровень проверки:", value="Высокий", inline=True)
        elif temp == discord.VerificationLevel.very_high:
            embed.add_field(name="Уровень проверки:", value="Очень высокий", inline=True)
        embed.add_field(name="Дата создания:", value=f"{discord.utils.format_dt(interaction.guild.created_at, 'D')} ({discord.utils.format_dt(interaction.guild.created_at, 'R')})", inline=True)
        if interaction.guild.rules_channel != None:
            embed.add_field(name="Канал с правилами:", value=interaction.guild.rules_channel.mention)
        else:
            embed.add_field(name="Канал с правилами:", value="Недоступно (сервер не является сервером сообщества)")
        roles = ""
        counter = 0
        guild_roles = await interaction.guild.fetch_roles()
        for role in guild_roles:
            if counter == 0:
                counter += 1
                continue
            if counter <= 15:
                roles += f"{role.mention}, "
            else:
                roles += f"и ещё {len(guild_roles) - 16}..."
                break
            counter += 1
        embed.add_field(name=f"Роли ({len(interaction.guild.roles) - 1}):", value=roles)
        if interaction.guild.icon != None:
            embed.set_thumbnail(url=interaction.guild.icon.replace(static_format="png", size=1024))
        if interaction.guild.banner != None:
            embed.set_image(url=interaction.guild.banner.replace(static_format="png"))
        embed.set_footer(text=f"ID: {interaction.guild.id}")

        if interaction.guild.banner != None:
            banner = discord.Embed(color=discord.Color.orange(), description=f"[Скачать]({interaction.guild.banner.url})")
            banner.set_author(name=f"Баннер {interaction.guild.name}")
            banner.set_image(url=interaction.guild.banner.url)
        else:
            banner = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У сервера отсутствует баннер!")

        if interaction.guild.icon != None:
            icon = discord.Embed(color=discord.Color.orange(), description=f"[Скачать]({interaction.guild.icon.url})")
            icon.set_author(name=f"Аватар {interaction.guild.name}")
            icon.set_image(url=interaction.guild.icon.url)
        else:
            icon = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У сервера отсутствует аватар!")

        class SelectMenu(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Аватар", value="avatar", description="Получить аватар сервера.", emoji="🖼️"),
                    discord.SelectOption(label="Баннер", value="banner", description="Получить баннер сервера (при наличии).", emoji="🏙️"),
                    discord.SelectOption(label="Информация", value="main", description="Информация об сервере.", emoji="📙")
                ]
                super().__init__(placeholder="Информация...", min_values=1, max_values=1, options=options)
            
            async def callback(self, viewinteract: discord.Interaction):
                if self.values[0] == "main":
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                elif self.values[0] == "avatar":
                    await viewinteract.response.send_message(embed=icon, ephemeral=True)
                else:
                    await viewinteract.response.send_message(embed=banner, ephemeral=True)

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(SelectMenu())

        await interaction.response.send_message(embed=embed, view=View())

    @app_commands.command(name="botinfo", description="[Полезности] Информация о боте")
    @app_commands.check(is_shutted_down)
    async def botinfo(self, interaction: discord.Interaction):
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = discord.Embed(title=f"{self.bot.user.name} - v{settings['curr_version']}", color=discord.Color.orange(), description=f"Для выбора категории используйте меню снизу.\n\n**Основная информация:**")
        embed.add_field(name="Разработчик:", value=f"<@!{settings['owner_id']}>")
        embed.add_field(name="ID разработчика:", value=f"`{settings['owner_id']}`")
        embed.add_field(name="ID бота:", value=f"`{self.bot.user.id}`")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"©️ 2021 - 2022 {self.bot.user.name}")

        stats = discord.Embed(title=f"{self.bot.user.name} - Статистика", color=discord.Color.orange())
        stats.add_field(name="Пинг:", value=f"{int(round(self.bot.latency, 3)*1000)}ms")
        stats.add_field(name="Запущен:", value=f"<t:{started_at}:R>")
        stats.add_field(name="Кол-во серверов:", value=len(self.bot.guilds))
        stats.add_field(name="Кол-во участников:", value=len(self.bot.users))
        stats.add_field(name="Последняя использованная команда:", value=config.lastcommand)
        stats.add_field(name="Кол-во команд/контекстных меню:", value=f"{len(self.bot.tree.get_commands(type=discord.AppCommandType.chat_input))}/{len(self.bot.tree.get_commands(type=discord.AppCommandType.user)) + len(self.bot.tree.get_commands(type=discord.AppCommandType.message))}")
        stats.add_field(name="Обработано команд:", value=config.used_commands)
        stats.set_thumbnail(url=self.bot.user.display_avatar.url)
        stats.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)

        versions = discord.Embed(title=f"{self.bot.user.name} - Версии", color=discord.Color.orange())
        versions.add_field(name="Версия:", value=settings['curr_version'])
        versions.add_field(name="Версия discord.py:", value=f"{discord.version_info.major}.{discord.version_info.minor}.{discord.version_info.micro} `{discord.version_info.releaselevel.upper()}`")
        versions.add_field(name="Версия Python:", value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        ver_info = sys.platform
        if ver_info.startswith("win32"):
            ver_info = "Windows"
        if ver_info.startswith("linux"):
            ver_info = "Linux"
        if ver_info.startswith("aix"):
            ver_info = "AIX"
        if ver_info.startswith("darwin"):
            ver_info = "MacOS"
        versions.add_field(name="Операционная система:", value=ver_info)
        versions.set_thumbnail(url=self.bot.user.display_avatar.url)
        versions.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)

        boticordinfo: boticordpy.types.Bot = await self.boticord_client.get_bot_info(880911386916577281)
        boticord = discord.Embed(
            title = "MadBot - Boticord",
            color = discord.Color.orange(),
            url=f"https://boticord.top/bot/{boticordinfo.short_code}",
            description=boticordinfo.long_description
        )
        boticord.add_field(name="Кол-во апов:", value=f"`{boticordinfo.bumps}`.")
        boticord.add_field(name="Кол-во добавлений:", value=f"`{boticordinfo.added}`")
        boticord.add_field(name="Теги:", value=f"`{str(boticordinfo.tags).removeprefix('[').removesuffix(']')}`")
        boticord.add_field(name="Статус рассмотрения:", value=f"`{boticordinfo.status}`")
        boticord.add_field(name="Короткое описание:", value=f"`{boticordinfo.short_description}`")
        boticord.add_field(name="Короткий код бота на сайте:", value=f"`{boticordinfo.short_code}`")
        boticord.set_thumbnail(url=self.bot.user.display_avatar.url)
        boticord.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)

        embeds = {
            'embed': embed,
            'stats': stats,
            'versions': versions,
            'boticord': boticord
        }

        class DropDown(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Главная", value="embed", description="Главное меню.", emoji="🐱"),
                    discord.SelectOption(label="Статистика", value='stats', description="Статистика бота.", emoji="📊"),
                    discord.SelectOption(label="Версии", value="versions", description="Версии библиотек и Python.", emoji="⚒️"),
                    discord.SelectOption(label="Boticord", value="boticord", description="Информация из Boticord.", emoji="<:bc:947181639384051732>")
                ]
                super().__init__(placeholder="Выбор...", options=options, row=1)

            async def callback(self, viewinteract: discord.Interaction):
                if interaction.user != viewinteract.user:
                    return await viewinteract.response.send_message(embed=embeds[self.values[0]], ephemeral=True)
                else:
                    await interaction.edit_original_message(embed=embeds[self.values[0]])
                    await viewinteract.response.defer()

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(discord.ui.Button(label="Поддержка", url=settings['support_invite']))
                self.add_item(discord.ui.Button(label="Добавить бота", url=f"https://discord.com/oauth2/authorize?client_id={settings['app_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands"))
                self.add_item(discord.ui.Button(label="Апнуть бота: BotiCord.top", url="https://boticord.top/bot/madbot", emoji="<:bc:947181639384051732>"))
                self.add_item(discord.ui.Button(label="Апнуть бота: SDC Monitoring", url="https://bots.server-discord.com/880911386916577281", emoji="<:favicon:981586173204000808>"))
                self.add_item(DropDown())

        await interaction.response.send_message(embed=embed, view=View())
        config.lastcommand = "`/botinfo`"
        config.used_commands += 1

    @app_commands.command(name="badgeinfo", description="[Полезности] Информация о значках пользователей и серверов в боте.")
    @app_commands.check(is_shutted_down)
    async def badgeinfo(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/badgeinfo`"
        embed=discord.Embed(title="Виды значков:", color=discord.Color.orange())
        embed.add_field(name="Значки пользователя:", value=f"<:ban:946031802634612826> - пользователь забанен в системе бота.\n<:timeout:950702768782458893> - пользователь получил тайм-аут на сервере.\n<:botdev:977645046188871751> - разработчик бота.\n<:code:946056751646638180> - помощник разработчика.\n<:support:946058006641143858> - поддержка бота.\n<:bug_hunter:955497457020715038> - охотник на баги (обнаружил и сообщил о 3-х и более багах).\n<:bug_terminator:955891723152801833> - уничтожитель багов (обнаружил и сообщил о 10-ти и более багах).\n<:verified:946057332389978152> - верифицированный пользователь.\n<:bot:946064625525465118> - участник является ботом.", inline=False)
        embed.add_field(name="Значки сервера:", value=f"<:verified:946057332389978152> - верифицированный сервер.\n<:ban:946031802634612826> - сервер забанен в системе бота.\n<:beta:946063731819937812> - сервер, имеющий доступ к бета-командам.", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='outages', description="[Полезности] Показывает актуальные сбои в работе бота.")
    @app_commands.check(is_shutted_down)
    async def outages(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/outages`'
        channel = await self.bot.fetch_channel(settings['outages'])
        outage = None
        async for message in channel.history(limit=1):
            outage = message
        if message.content.find("<:outage_fixed:958778052136042616>") == -1:
            embed = discord.Embed(title="Обнаружено сообщение о сбое!", color=discord.Color.red(), description=outage.content, timestamp=outage.created_at)
            embed.set_author(name=outage.author, icon_url=outage.author.display_avatar.url)
            embed.set_footer(text="Актуально на")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Актуальные сбои отсутствуют", color=discord.Color.green(), description="Спасибо, что пользуетесь MadBot!", timestamp=discord.utils.utcnow())
            embed.set_footer(text="Актуально на")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nick", description="[Полезности] Изменяет ваш ник.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(argument="Ник, на который вы хотите поменять. Оставьте пустым для сброса ника")
    async def nick(self, interaction: discord.Interaction, argument: str = None):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/nick`"
        if argument != None:
            if len(argument) > 32:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Длина ника не должна превышать `32 символа`!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.user.guild_permissions.change_nickname:
            if interaction.user.id == interaction.guild.owner.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Бот не может изменять никнейм владельцу сервера!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            try:
                await interaction.user.edit(nick=argument, reason="Самостоятельная смена ника")
            except Forbidden:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не смог изменить вам никнейм!\nТип ошибки: `Forbidden`")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = None
                if argument != None:
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Ваш ник успешно изменён на `{argument}`!", timestamp=discord.utils.utcnow())
                else:
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Ваш ник успешно сброшен!", timestamp=discord.utils.utcnow())
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            string = None
            if argument == None:
                string = "Вы желаете сбросить никнейм."
            else:
                string = f"Ваш желаемый ник: `{argument}`."
            embed = discord.Embed(title="Запрос разрешения", color=discord.Color.orange(), description=f"Вы не имеете права на `изменение никнейма`. Попросите участника с правом на `управление никнеймами` разрешить смену ника.\n{string}")
            embed.set_footer(text="Время ожидания: 5 минут.")
            
            class NickButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                    self.value = None

                @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
                async def confirm(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    if viewinteract.user.guild_permissions.manage_nicknames:
                        self.value = True
                        try:
                            await interaction.user.edit(nick=argument, reason=f"Одобрено // {viewinteract.user}")
                        except Forbidden:
                            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права `управление никнеймами`.\nКод ошибки: `Forbidden`.")
                            return await interaction.edit_original_message(embed=embed, view=None)
                        else:
                            embed = None
                            if argument != None:
                                embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Ваш ник успешно изменён на `{argument}`!", timestamp=discord.utils.utcnow())
                                embed.set_author(name=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                            else:
                                embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Ваш ник успешно сброшен!", timestamp=discord.utils.utcnow())
                                embed.set_author(name=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                            await interaction.edit_original_message(embed=embed, view=None)
                    else:
                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `управлять никнеймами` для использования кнопки!")
                        return await viewinteract.response.send_message(embed=embed, ephemeral=True)

                @discord.ui.button(emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.red)
                async def denied(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    if viewinteract.user.guild_permissions.manage_nicknames:
                        self.value = False
                        embed = discord.Embed(title="Отказ", color=discord.Color.red(), description="Вам отказано в смене ника!")
                        embed.set_author(name=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                        return await interaction.edit_original_message(embed=embed, view=None)
                    else:
                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `управлять никнеймами` для использования кнопки!")
                        return await viewinteract.response.send_message(embed=embed, ephemeral=True)
            
            await interaction.response.send_message(embed=embed, view=NickButtons())
            await NickButtons().wait()
            if NickButtons().value == None:
                embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
                await interaction.edit_original_message(embed=embed, view=None)

    @app_commands.command(name="idea", description="[Полезности] Предложить идею для бота.")
    @app_commands.check(is_shutted_down)
    @app_commands.checks.dynamic_cooldown(cooldown_check)
    @app_commands.describe(title="Суть идеи", description="Описание идеи", attachment="Изображение для показа идеи")
    async def idea(self, interaction: discord.Interaction, title: str, description: str, attachment: typing.Optional[discord.Attachment]):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/idea`'
        idea_embed = discord.Embed(title=title, color=discord.Color.orange(), description=description, timestamp=discord.utils.utcnow())
        idea_embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar)
        if attachment != None:
            idea_embed.set_image(url=attachment.url)
        channel = self.bot.get_channel(settings['idea_channel'])
        message = await channel.send(embed=idea_embed)
        await message.add_reaction("✅")
        await message.add_reaction("💤")
        await message.add_reaction("❌")
        embed = discord.Embed(title='Успешно!', color=discord.Color.green(), description="Идея отправлена в канал")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="getemoji", description="[Полезности] Выдает эмодзи картинкой.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(emoji_name="Название, ID либо сам эмодзи.", is_registry="Стоит ли учитывать регистр имени?")
    async def getemoji(self, interaction: discord.Interaction, emoji_name: str, is_registry: bool = False):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/getemoji`'
        embeds = []
        for emoji in interaction.guild.emojis:
            x = emoji.name
            y = emoji_name
            z = str(emoji)
            if not is_registry:
                x = x.lower()
                y = y.lower()
                z = z.lower()
            if x == y or str(emoji.id) == y or z == y:
                try:
                    embed = discord.Embed(title="🤪 Информация об эмодзи", color=discord.Color.orange(), description=f"[Скачать]({emoji.url})")
                    embed.add_field(name="Название:", value=f"```\n{emoji.name}```")
                    embed.add_field(name="Вид без форматирования:", value=f"```\n{str(emoji)}```")
                    embed.set_footer(text=f"ID: {emoji.id}")
                    embed.set_thumbnail(url=emoji.url)
                    if len(embeds) == 9:
                        embed.set_footer(text="Это максимальное кол-во эмодзи, которое может быть выведено за раз.")
                    if len(embeds) != 10:
                        embeds.append(embed)
                except Forbidden:
                    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет доступа к файлу эмодзи.\nТип ошибки: `Forbidden`.")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Эмодзи с данным именем не был обнаружен!\nТип ошибки: `NotFound`.")
        if len(embeds) == 0:
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.send_message(embeds=embeds)

    @app_commands.command(name="send", description="[Полезности] Отправляет сообщение в канал от имени вебхука")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(message="Сообщение, которое будет отправлено")
    async def send(self, interaction: discord.Interaction, message: str):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/send`'
        if interaction.channel.permissions_for(interaction.guild.get_member(self.bot.user.id)).manage_webhooks == False:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на управление вебхуками!\nТип ошибки: `Forbidden`.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        webhook = None
        webhooks = await interaction.channel.webhooks()
        for hook in webhooks:
            if hook.name == "MadWebHook":
                webhook = hook
                break
        if webhook == None:
            webhook = await interaction.channel.create_webhook(name="MadWebHook")
        await webhook.send(message, username=interaction.user.name, avatar_url=interaction.user.display_avatar.url)
        embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Сообщение успешно отправлено!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="getaudit", description="[Полезности] Получает информацию о кол-ве модерационных действий пользователя.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member="Участник, чьё кол-во действий вы хотите увидить")
    async def getaudit(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/getaudit`'
        if interaction.user.guild_permissions.view_audit_log:
            member_bot = await interaction.guild.fetch_member(self.bot.user.id)
            if member_bot.guild_permissions.view_audit_log == False:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет доступа к журналу аудита!\nТип ошибки: `Forbidden`.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            embed = discord.Embed(title="В процессе...", color=discord.Color.yellow(), description=f"Собираем действия участника {member.mention}...")
            await interaction.response.send_message(embed=embed)
            entries = [entry async for entry in interaction.guild.audit_logs(limit=None, user=member)]
            embed = discord.Embed(title="Готово!", color=discord.Color.green(), description=f"Бот смог насчитать `{len(entries)}` действий от участника {member.mention}.")
            await interaction.edit_original_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `просмотр журнала аудита` для выполнения этой команды!")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="weather", description="[Полезности] Узнать погоду в городе.")
    @app_commands.describe(city="Город, где надо узнать погоду")
    @app_commands.check(is_shutted_down)
    async def weather(self, interaction: discord.Interaction, city: str):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/weather`'
        city = city.replace(' ', '%20')
        embed = discord.Embed(title="Поиск...", color=discord.Color.yellow(), description="Ищем ваш город...")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&APPID={settings['weather_key']}&units=metric&lang=ru")
        json = response.json()
        if response.status_code > 400:
            if json['message'] == "city not found":
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Город не найден!")
                return await interaction.edit_original_message(embed=embed)
            else:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось узнать погоду! Код ошибки: `{json['cod']}`")
                print(f"{json['cod']}: {json['message']}")
                return await interaction.edit_original_message(embed=embed)
        else:
            embed = discord.Embed(title=f"Погода в {json['name']}", color=discord.Color.orange(), description=f"{json['weather'][0]['description']}", url=f"https://openweathermap.org/city/{json['id']}")
            embed.add_field(name="Температура:", value=f"{int(json['main']['temp'])}°С ({int(json['main']['temp_min'])}°С / {int(json['main']['temp_max'])}°С)")
            embed.add_field(name="Ощущается как:", value=f"{int(json['main']['feels_like'])}°С")
            embed.add_field(name="Влажность:", value=f"{json['main']['humidity']}%")
            embed.add_field(name="Скорость ветра:", value=f"{json['wind']['speed']}м/сек")
            embed.add_field(name="Облачность:", value=f"{json['clouds']['all']}%")
            embed.add_field(name="Рассвет/Закат:", value=f"<t:{json['sys']['sunrise']}> / <t:{json['sys']['sunset']}>")
            embed.set_footer(text="В целях конфиденциальности, ответ виден только вам. Бот не сохраняет информацию о запрашиваемом городе.")
            embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{json['weather'][0]['icon']}@2x.png")
            await interaction.edit_original_message(embed=embed)
    
    @app_commands.command(name="stopwatch", description="[Полезности] Секундомер.")
    @app_commands.check(is_shutted_down)
    async def stopwatch(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/stopwatch`'
        embed = discord.Embed(title="Секундомер", color=discord.Color.orange(), description=f"Время пошло!\nСекундомер запущен {discord.utils.format_dt(discord.utils.utcnow(), 'R')}")
        embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)\

        class Button(discord.ui.View):
            def __init__(self, start):
                super().__init__(timeout=None)
                self.start = start

            @discord.ui.button(label="Стоп", style=discord.ButtonStyle.danger)
            async def callback(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != viewinteract.user.id:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                stop = time.time() - self.start
                embed = discord.Embed(title="Секундомер остановлен!", color=discord.Color.red(), description=f"Насчитанное время: `{round(stop, 3)}s`.")
                embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
                button.disabled = True
                await viewinteract.response.edit_message(embed=embed, view=self)

        start = time.time()
        await interaction.response.send_message(embed=embed, view=Button(start))

    @app_commands.command(name="debug", description="[Полезности] Запрос основной информации о боте.")
    @app_commands.check(is_shutted_down)
    @app_commands.checks.dynamic_cooldown(cooldown_check)
    async def debug(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/debug`'

        def get_permissions(perms: discord.Permissions):
            ans = ""
            ans += f"✅ Отправка сообщений\n" if perms.send_messages else f"❌ Отправка сообщений\n"
            ans += f"✅ Добавление ссылок\n" if perms.embed_links else f"❌ Добавление ссылок\n"
            ans += f"✅ Использование внешних эмодзи\n" if perms.use_external_emojis else f"❌ Использование внешних эмодзи\n"
            ans += f"✅ Управление каналами\n" if perms.manage_channels else f"❌ Управление каналами\n"
            ans += f"✅ Исключение участников\n" if perms.kick_members else f"❌ Исключение участников\n"
            ans += f"✅ Блокировка участников\n" if perms.ban_members else f"❌ Блокировка участников\n"
            ans += f"✅ Чтение истории сообщений\n" if perms.read_message_history else f"❌ Чтение истории сообщений\n"
            ans += f"✅ Чтение сообщений\n" if perms.read_messages else f"❌ Чтение сообщений\n"
            ans += f"✅ Управление участниками\n" if perms.moderate_members else f"❌ Управление участниками\n"
            ans += f"✅ Управление никнеймами\n" if perms.manage_nicknames else f"❌ Управление никнеймами\n"
            ans += f"✅ Управление сообщениями\n" if perms.manage_messages else f"❌ Управление сообщениями\n"
            ans += f"✅ Создание приглашений\n" if perms.create_instant_invite else f"❌ Создание приглашений\n"
            ans += f"✅ Управление сервером\n" if perms.manage_guild else f"❌ Управление сервером\n"
            ans += f"✅ Управление вебхуками\n" if perms.manage_webhooks else f"❌ Управление вебхуками\n"
            ans += f"✅ Журнал аудита\n" if perms.view_audit_log else f"❌ Журнал аудита\n"
            return ans

        embed = discord.Embed(title="Отладка", color=discord.Color.orange())
        embed.add_field(
            name="Права бота",
            value=get_permissions(interaction.guild.get_member(self.bot.user.id).guild_permissions)
        )
        embed.add_field(
            name="Права в этом канале",
            value=get_permissions(interaction.channel.permissions_for(interaction.guild.get_member(self.bot.user.id)))
        )
        embed.add_field(
            name="Информация о сервере",
            value=(f"Имя канала:\n`{interaction.channel.name}`\nID канала:\n`{interaction.channel.id}`\n" +
                f"Кол-во каналов:\n`{len(interaction.guild.channels)}/500`\n" + 
                f"Название сервера:\n`{interaction.guild.name}`\nID сервера:\n`{interaction.guild.id}`"
            )
        )
        ans = ''
        ans += f"✅ Создатель\n" if interaction.user.id == interaction.guild.owner.id else f"❌ Создатель\n"
        ans += f"✅ Администратор\n" if interaction.user.guild_permissions.administrator else f"❌ Администратор\n"
        embed.add_field(
            name="Информация о пользователе",
            value=f"Пользователь:\n`{interaction.user}`\nID пользователя:\n`{interaction.user.id}`\nПрава:\n`{ans}`"
        )
        channel = self.bot.get_channel(settings['debug_channel'])
        message = await channel.send(embed=embed)
        await interaction.response.send_message(content=f"Если поддержка запросила ссылку с команды, отправьте ей это: {message.jump_url}",embed=embed)

    @app_commands.command(name="autorole", description="[Полезности] Настроить выдачу ролей по нажатию кнопки.")
    @app_commands.describe(
        title='Название эмбеда',
        description='Содержание эмбеда',
        role1='Роль для выдачи', 
        role2='Роль для выдачи',
        role3='Роль для выдачи',
        role4='Роль для выдачи',
        role5='Роль для выдачи',
        role6='Роль для выдачи',
        role7='Роль для выдачи',
        role8='Роль для выдачи',
        role9='Роль для выдачи',
        role10='Роль для выдачи',
        role11='Роль для выдачи',
        role12='Роль для выдачи',
        role13='Роль для выдачи',
        role14='Роль для выдачи',
        role15='Роль для выдачи',
        role16='Роль для выдачи',
        role17='Роль для выдачи',
        role18='Роль для выдачи',
        role19='Роль для выдачи',
        role20='Роль для выдачи',
        role21='Роль для выдачи',
        role22='Роль для выдачи',
        role23='Роль для выдачи'
    )
    @app_commands.check(is_shutted_down)
    async def autorole(
        self, 
        interaction: discord.Interaction, 
        title: str,
        description: str,
        role1: discord.Role, 
        role2: typing.Optional[discord.Role],
        role3: typing.Optional[discord.Role],
        role4: typing.Optional[discord.Role],
        role5: typing.Optional[discord.Role],
        role6: typing.Optional[discord.Role],
        role7: typing.Optional[discord.Role],
        role8: typing.Optional[discord.Role],
        role9: typing.Optional[discord.Role],
        role10: typing.Optional[discord.Role],
        role11: typing.Optional[discord.Role],
        role12: typing.Optional[discord.Role],
        role13: typing.Optional[discord.Role],
        role14: typing.Optional[discord.Role],
        role15: typing.Optional[discord.Role],
        role16: typing.Optional[discord.Role],
        role17: typing.Optional[discord.Role],
        role18: typing.Optional[discord.Role],
        role19: typing.Optional[discord.Role],
        role20: typing.Optional[discord.Role],
        role21: typing.Optional[discord.Role],
        role22: typing.Optional[discord.Role],
        role23: typing.Optional[discord.Role]
    ):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True) 
        config.lastcommand = '`/autorole`'
        if interaction.user.guild_permissions.manage_roles:
            bot_member = await interaction.guild.fetch_member(self.bot.user.id)
            if not(bot_member.guild_permissions.manage_roles):
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Бот не имеет права `управлять ролями`, что необходимо для работы команды!"
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            roles = [
                role1, role2, role3, role4, role5,
                role6, role7, role8, role9, role10,
                role11, role12, role13, role14, role15,
                role16, role17, role18, role19, role20,
                role21, role22, role23
            ]
            class View(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
            view = View()
            for role in roles:
                role: discord.Role
                if role != None:
                    if role.position == 0:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Ты кому собираешься выдавать @everyone?)"
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    if bot_member.top_role <= role:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description=f"Роль {role.mention} выше роли бота, поэтому бот не сможет выдать её кому-либо."
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    if role.is_bot_managed():
                        embed = discord.Embed(
                            title="Ошибка!", 
                            color=discord.Color.red(),
                            description=f"Роль {role.mention} является ролью интеграции, поэтому выдать её кому-либо нельзя!"
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    view.add_item(
                        discord.ui.Button(
                            label=role.name, 
                            style=discord.ButtonStyle.blurple,
                            custom_id=str(role.id)
                        )
                    )
            class AcceptRules(discord.ui.View):
                def __init__(self, bot: commands.Bot):
                    super().__init__(timeout=60)
                    self.value = None
                    self.bot = bot
                
                @discord.ui.button(style=discord.ButtonStyle.green, emoji="✅")
                async def accept(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    nonlocal view
                    self.value = True
                    embed = discord.Embed(
                        title=title,
                        color=discord.Color.orange(),
                        description=description
                    )
                    embed.set_footer(text=f"Создал: {interaction.user}", icon_url=interaction.user.display_avatar.url)
                    try:
                        await viewinteract.channel.send(embed=embed, view=view)
                    except:
                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Бот не имеет права на отправку сообщения в этом канале!")
                        return await viewinteract.response.edit_message(embed=embed, view=None)
                    log_channel = self.bot.get_channel(settings['log_channel'])
                    await log_channel.send(content=f"`{interaction.user}` на сервере `{interaction.guild.name}` создал выдачу ролей! Их эмбед:", embed=embed)
                    embed = discord.Embed(
                        title="Успешно!",
                        color=discord.Color.green(),
                        description="Выдача ролей успешно настроена!"
                    )
                    await viewinteract.response.edit_message(embed=embed, view=None)
                
                @discord.ui.button(style=discord.ButtonStyle.red, emoji="<:x_icon:975324570741526568>")
                async def deny(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    self.value = False
                    embed = discord.Embed(title="Отмена!", color=discord.Color.red(), description="Выдача ролей по реакциям отменена!")
                    await viewinteract.response.edit_message(embed=embed, view=None)
            
            embed = discord.Embed(
                title="Обязательно к прочтению!",
                color=discord.Color.orange(),
                description=f"Мы, простые разработчики бота, просим не использовать в кастомизированном эмбеде что-либо, нарушающее правила Discord. В противном случае, Ваш сервер и Ваш аккаунт будут занесены в черный список бота.\nВы согласны с требованиями?"
            )
            waiting = AcceptRules(bot=self.bot)
            await interaction.response.send_message(embed=embed, ephemeral=True, view=waiting)
            await waiting.wait()
            if waiting.value == None:
                embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
                await interaction.edit_original_message(embed=embed, view=None)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `управлять ролями` для использования команды!")
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tools(bot))
    print('Cog "Tools" запущен!')