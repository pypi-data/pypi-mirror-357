import re

from openpyxl.cell import Cell


def extract_rgb_key(cell: Cell) -> str | None:
    fill = cell.fill
    if fill is None or fill.fill_type != "solid":
        return None

    color = fill.fgColor
    if color.type == "rgb" and color.rgb is not None:
        return color.rgb.upper()
    return None


def clean_spaces(s: str) -> str:
    # Убираем лишние пробелы внутри строки
    return re.sub(r'\s+', ' ', s).strip()


def join_dicts(dict1: dict, dict2: dict):
    if (not dict1) and (not dict2):
        return dict()
    if not dict1:
        return dict2
    if not dict2:
        return dict1

    merged_dict = {}
    for key, values in dict1.items():
        merged_dict[key] = values.copy()

    for key, values in dict2.items():
        if key in merged_dict:
            merged_dict[key].extend(values)
        else:
            merged_dict[key] = values

    for key in merged_dict:
        merged_dict[key] = list(set(merged_dict[key]))
    return merged_dict
