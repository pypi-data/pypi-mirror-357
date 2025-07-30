from dataclasses import dataclass

from dubna_parser.enums import WeekDay, Type

@dataclass(slots=True)
class Group:
    """группа"""
    group: int = 0
    specialization: str = 'undefined'

    def __eq__(self, other):
        return self.group == other.group

    def __hash__(self):
        return hash(self.group)

@dataclass(slots=True)
class Pair:
    """сущность пары """
    classroom: str = 'undefined'
    subject: str = 'undefined'
    teacher: str = 'undefined'
    type_: Type = Type.DEFAULT

    def __str__(self):
        return f"{self.classroom} - {self.subject} - {self.teacher}"


# выше две базовые сущности
@dataclass(slots=True)
class AlternatingPair:
    """пара мигалка, которая состоит из двух пар"""
    odd_week: Pair | None  # нечётная неделя
    even_week: Pair | None  # чётная неделя

@dataclass(slots=True)
class SchedulePair:
    """определённая пара в расписании"""
    pair_number: int
    pair: AlternatingPair | Pair | None

@dataclass(slots=True)
class MergedPairs:
    groups: list[Group]
    pair: SchedulePair
    weekday: WeekDay

@dataclass(slots=True)
class GroupPairs:
    """расписание группы для определённой группы на неделю"""
    group: Group
    group_pairs: dict[WeekDay, list[SchedulePair]]

@dataclass(slots=True)
class Schedule:
    specializations_with_groups_from_file: dict[str, list[Group]]
    specializations: list[str] | set[str]
    groups: list[Group] | set[Group]
    classrooms: list[str] | set[str]
    teachers: list[str] | set[str]
    subjects: list[str] | set[str]
    schedule_pairs: list[GroupPairs]
    merged_pairs: dict[str, list[Group]]
