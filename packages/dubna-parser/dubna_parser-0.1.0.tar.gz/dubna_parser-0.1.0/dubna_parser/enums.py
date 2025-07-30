from enum import Enum


class WeekDay(str, Enum):
    MONDAY = "понедельник"
    TUESDAY = "вторник"
    WEDNESDAY = "среда"
    THURSDAY = "четверг"
    FRIDAY = "пятница"
    SATURDAY = "суббота"
    SUNDAY = "воскресенье"


class Type(str, Enum):
    LECTURE = "лекция"
    SEMINAR = "семинар"
    DOT = "ДОТ"
    PHYSICAL = "физическая культура"
    DEFAULT = "неизвестно"

