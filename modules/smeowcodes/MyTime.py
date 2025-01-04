# ---------------------------------------------------------------------------------
#  /\_/\  🌐 This module was loaded through https://t.me/hikkamods_bot
# ( o.o )  🔐 Licensed under the GNU AGPLv3.
#  > ^ <   ⚠️ Owner of heta.hikariatama.ru doesn't take any responsibilities or intellectual property rights regarding this script
# ---------------------------------------------------------------------------------
# Name: MyTime
# Description: Чючют крутой модуль
# Author: skillzmeow
# Commands:
# .mytime | .timezones
# ---------------------------------------------------------------------------------


__version__ = (2, 0, 1)

# module by:
# █▀ █▄▀ █ █░░ █░░ ▀█
# ▄█ █░█ █ █▄▄ █▄▄ █▄

# █▀▄▀█ █▀▀ █▀█ █░█░█
# █░▀░█ ██▄ █▄█ ▀▄▀▄▀
#   you can edit this module
#            2022
# 🔒 Licensed under the AGPL-3.0
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @smeowcodes

import calendar as c
import datetime
import logging
import random

import pytz
from pytz import timezone
from telethon.tl.types import Message

from .. import loader, main, utils
from ..inline.types import InlineCall, InlineQuery

logger = logging.getLogger(__name__)


class MyTimeMod(loader.Module):
    """Чючют крутой модуль"""

    strings = {
        "name": "MyTime",
        "time": "📡 Accuracy time",
        "cancel_btn": "🚫 Close",
        "back_btn": "⏪ Back",
        "datendtime": "📆 DateTime",
        "timezone": "🌞 All timezones",
        "datecalc": "🧑‍💻 DateCalculator",
        "date": "📆 Date",
        "open_manager": "📓 Open manager",
        "expected_date": "😀 Expected date",
        "calendar": "🗓 Calendar",
        "ss": "{} days, {} hours, {} minutes.",
        "wyc": "What you choose?😅",
        "days": "Mon, Tue, Wed, Thu, Fri, Sat, Sun",
        "month": (
            "January, February, March, April, May, June, July, August, September,"
            " October, November, December"
        ),
    }
    strings_ru = {
        "time": "📡 Точное время",
        "cancel_btn": "🚫 Закрыть",
        "back_btn": "⏪ Назад",
        "datendtime": "📆 Дата и время",
        "timezone": "🌞 Все таймзоны",
        "datecalc": "🧑‍💻 Счётчик дат",
        "date": "📆 Дата",
        "open_manager": "📓 Открыть менеджер",
        "expected_date": "😀 Ожидаемая дата",
        "calendar": "🗓 Календарь",
        "ss": "{} дней, {} часов, {} минут.",
        "wyc": "Что выберешь?😅",
        "days": "Пн , Вт , Ср , Чт , Пт , Сб , Вс ",
        "month": (
            "Январь, Февраль, Март, Апрель, Май, Июнь, Июль, Август, Сентябрь, Октябрь,"
            " Ноябрь, Декабрь"
        ),
    }
    strings_ua = {
        "time": "📡 Точний час",
        "cancel_btn": "🚫 Зачинити",
        "back_btn": "⏪ Назад",
        "datendtime": "📆 Дата і час",
        "timezone": "🌞 Всі таймзони",
        "datecalc": "🧑‍💻 Лічільник дат",
        "date": "📆 Дата",
        "open_manager": "📓 Відкрити менеджер",
        "expected_date": "😀 Очікувана дата",
        "calendar": "🗓 Календар",
        "ss": "{} днів, {} годин, {} хвилин",
        "wyc": "Що вибереш?😅",
        "days": "Пн , Вт , Ср , Чт , Пт , Сб , Нд ",
        "month": (
            "Січень, Лютий, Березень, Квітень, Травень, Червень, Липень, Серпень,"
            " Вересень, Жовтень, Листопад"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "expected_date",
                "2023, 1, 1",
                lambda: "Укажите дату ЧЕРЕЗ запятую (year, month, day)",
            ),
            loader.ConfigValue(
                "datetext",
                "🎄 До нового года осталось",
                lambda: (
                    "Укажите текст для для вашей даты (До моего дня рождения осталось,"
                    " и тд)"
                ),
            ),
            loader.ConfigValue(
                "correct_time",
                "Europe/Moscow",
                lambda: (
                    "To check all timezones use:\n.e import pytz\npytz.all_timezones"
                ),
            ),
        )

    @staticmethod
    async def cancel(call: InlineCall):
        await call.delete()

    @loader.unrestricted
    async def mytimecmd(self, message: Message):
        "open a manager"
        list = [
            "модуль от скиллза",
            "в хикке только кнопочки и смайлики...",
            "че за хрень?",
            "хочу фтг",
            "ваша сессия спижжена скилзом",
        ]
        hz = random.choice(list)
        args = utils.get_args_raw(message)
        if not args:
            await self.inline.form(
                message=message,
                text=f"<b>{hz}</b>",
                reply_markup=[
                    [
                        {
                            "text": self.strings("open_manager"),
                            "callback": self.back_btn,
                        },
                    ],
                ],
            )
        else:
            await utils.answer(message, "эм чо хочещ")

    async def time_call(self, call: InlineCall) -> None:
        tz = timezone(self.config["correct_time"])
        timenow = datetime.datetime.now(tz)
        time = timenow.strftime("%H:%M:%S")
        date = timenow.strftime("%d.%m.%Y")

        await call.edit(
            text=(
                f"\n<b>{self.strings('date')}: {date}\n\n{self.strings('time')}:"
                f" {time}</b>"
            ),
            reply_markup=[
                [
                    {
                        "text": self.strings("back_btn"),
                        "callback": self.back_btn,
                    },
                    {"text": self.strings("cancel_btn"), "callback": self.cancel},
                ],
            ],
        )

    async def expectedtime_call(self, call: InlineCall):
        stroka = str(self.config["expected_date"])
        tz = timezone(self.config["correct_time"])
        timenow = datetime.datetime.now(tz)
        n = datetime.datetime(*self.config["expected_date"], tzinfo=tz)
        d = n - timenow
        mm = divmod(d.seconds, 60)[0]
        hh, mm = divmod(mm, 60)
        await call.edit(
            text=(
                f"<b><u>{self.strings('datecalc')}</u>\n\n{self.config['datetext']}:</b>"
                f" <code>{self.strings('ss').format(d.days, hh, mm)}</code>"
            ),
            reply_markup=[
                [
                    {
                        "text": self.strings("back_btn"),
                        "callback": self.back_btn,
                    },
                    {
                        "text": self.strings("cancel_btn"),
                        "callback": self.cancel,
                    },
                ],
            ],
        )
    
    async def calendar_call(self, call: InlineCall):
        mesaca = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        da = datetime.datetime.now()
        mo = da.strftime("%m")
        mont = int(mo.lstrip("0"))
        year = int(da.strftime("%Y"))
        list_month = self.strings("month").split(", ")
        name_month = c.month_name[int(mo)]
        index = mesaca.index(name_month)
        namemonth = list_month[index]

        b = c.monthcalendar(year, mont)

        days = self.strings("days").split(", ")

        form = (
            " ".join(days)
            + "\n"
            + "\n".join(
                "  ".join(
                    " •" if i == 0 else str(i) if len(str(i)) == 2 else " " + str(i)
                    for i in x
                )
                for x in b
            )
        )
        await call.edit(
            text=f"<b>🗓 {namemonth} {year}</b>\n<code>{form}</code>",
            reply_markup=[
                [
                    {
                        "text": self.strings("back_btn"),
                        "callback": self.back_btn,
                    },
                    {
                        "text": self.strings("cancel_btn"),
                        "callback": self.cancel,
                    },
                ],
            ],
        )

    async def timezonescmd(self, message: Message):
        await self.inline.form(
            message=message,
            text="Timezones",
            reply_markup=self._get_mark(),
            **({"photo": "https://0x0.st/oBvb.jpg"}),
        )

    async def back_btn(self, call: InlineCall):
        await call.edit(
            text=f"<b>{self.strings('wyc')}</b>",
            reply_markup=[
                [
                    {
                        "text": self.strings("datendtime"),
                        "callback": self.time_call,
                    },
                    {
                        "text": self.strings("datecalc"),
                        "callback": self.expectedtime_call,
                    },
                ],
                [{"text": self.strings("calendar"), "callback": self.calendar_call}],
                [{"text": self.strings("cancel_btn"), "callback": self.cancel}],
            ],
        )
