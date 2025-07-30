from dubna_parser.enums import Type

degrees = ['проф.', 'доцент', 'доц.', ' ст.пр.', 'пр.', 'ст.преподаватель', 'ст.преп.', 'профессор']

color_to_type = {"FFFFFF00": Type.LECTURE,
                 "FFEBF1DE": Type.PHYSICAL,
                 "FFEDE9F7": Type.DOT,
                 None: Type.SEMINAR,
                 "FFFFFFFF": Type.SEMINAR}
