# python minimal version: 3.8

from config import *
import datetime
import logging
import sqllex
import discord
from discord.ext import commands, tasks


formatter = logging.Formatter(f"[%(asctime)s %(filename)s %(funcName)s] %(levelname)s: %(message)s")

project_console_hl = logging.StreamHandler()
project_console_hl.setLevel("INFO")
project_console_hl.setFormatter(formatter)

project_file_hl = logging.FileHandler(filename="project.log", encoding="utf-8")
project_file_hl.setLevel("DEBUG")
project_file_hl.setFormatter(formatter)

logger = logging.getLogger("points")
logger.setLevel("DEBUG")
logger.addHandler(project_console_hl)
logger.addHandler(project_file_hl)

# libraries_file_hl = logging.FileHandler(filename="libraries.log", encoding="utf-8")
# libraries_file_hl.setLevel("DEBUG")
# libraries_file_hl.setFormatter(formatter)
#
# libraries_logger = logging.getLogger()
# libraries_logger.setLevel("DEBUG")
# libraries_logger.addHandler(libraries_file_hl)


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=command_prefix, activity=discord.Game(name="by Phizilion"), intents=intents)

db = sqllex.SQLite3x(path=db_path)
detectives = db["detectives"]


def is_admin(ctx):
    return ctx.author.id in admin_list


# функция обновления очков, отображающихся в сообщении
async def points_update():
    string = ""
    for i in detectives.select(SELECT=["nickname", "points", "week_points"]):
        string += f"{discord.utils.escape_markdown(i[0])}: {str(i[1])}({str(i[2])})\n"
    string += "Последний раз обновлено: " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")  # добавление времени
    msg = await bot.get_guild(detectives_guild_id).get_channel(points_channel_id).fetch_message(points_message_id)
    await msg.edit(content=string)
    logger.debug("очки обновлены успешно")


@bot.event
async def on_ready():
    logger.info("бот запущен")
    await points_update()
    new_week.start()
    logger.debug("запущен отсчёт недель")


# обработка новых отчётов
@bot.event
async def on_message(message):
    # нужное ли сообщение
    if message.channel.id != reports_channel_id:
        await bot.process_commands(message)  # начать обработку команд (при срабатывании on_message не работает)
        return
    if "<@" not in message.content:
        return
    # изменение бд
    detective_data = detectives.select(SELECT=["week_points", "nickname"], WHERE={"discord_id": message.author.id})[0]
    detectives.update(SET={"week_points": detective_data[0] + report_reward}, WHERE={"discord_id": message.author.id})
    # обновление + логи
    await points_update()
    await bot.get_channel(logs_channel_id).send(f"{detective_data[1]} выполнил вызов")
    await message.add_reaction(report_reaction)
    logger.debug(f"новый отчёт, {detective_data}")


# подсчёт очков за неделю
@tasks.loop(hours=168.0)
async def new_week():
    week_report_text = ""
    week_reward_report_text = "ЗП:\n"
    for i in detectives.select(SELECT=["id", "points", "week_points", "nickname", "salary"]):
        week_report_text += f"{discord.utils.escape_markdown(i[3])}: {i[1]} ({i[2]})\n"
        week_reward_report_text += f"{discord.utils.escape_markdown(i[3])}: {round((i[2] / report_reward * report_money_reward) + i[4])}\n"
        detectives.update(SET={"points": i[1] + i[2], "week_points": 0}, WHERE={"id": i[0]})
    await points_update()
    await bot.get_guild(detectives_guild_id).get_member(user_for_report).send(content=week_report_text + "\n" + week_reward_report_text)
    logger.info("начата новая неделя")


# ожидание до первой субботы
@new_week.before_loop
async def before_loop_new_week():
    now_calendar = datetime.datetime.now().isocalendar()
    if now_calendar[2] >= 7:
        end_of_week = datetime.datetime.fromisocalendar(now_calendar[0], now_calendar[1] + 1, 6)
    else:
        end_of_week = datetime.datetime.fromisocalendar(now_calendar[0], now_calendar[1], 6)
    end_of_week_second = end_of_week.replace(hour=23, minute=59, second=59, tzinfo=datetime.timezone(datetime.timedelta(hours=3)))
    logger.debug(f"следущая неделя - {end_of_week_second}")
    await discord.utils.sleep_until(end_of_week_second)


# команда подсчёта очков
@bot.command(name="new_week")
@commands.check(is_admin)
async def new_week_command(ctx):
    logger.info("команда новой недели")
    await new_week()
    await ctx.send(new_week_answer_message)


# ручное обновление
@bot.command()
@commands.check(is_admin)
async def update(ctx):
    logger.info("команда обновления")
    await points_update()
    await ctx.send(update_answer_message)


# da
@bot.command()
@commands.check(is_admin)
async def da(ctx):
    await ctx.send("da")


# выполнить sql код
@bot.command()
@commands.check(is_admin)
async def sql_execute(ctx, *, sql):
    req = db.execute(script=sql)
    await ctx.send("База данных вернула: " + str(req))
    logger.info(f"выполенен sql от {ctx.author.name} ({ctx.author.id}): {sql}, БД вернула: {str(req)}")


logger.debug("все переменные и функции успешно созданы")
bot.run(TOKEN)
