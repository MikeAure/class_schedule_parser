import pytz


class Class(dict):
    def __init__(self, class_abbr, class_name, location, teacher_name, score, total_periods, class_type):
        super().__init__()
        self["class_abbr"] = class_abbr
        self["class_name"]= class_name
        self["location"] = location
        self["teacher_name"] = teacher_name
        self["score"] = score
        self["total_periods"] = total_periods
        self["class_type"] = class_type

    # def __str__(self):
    #     return ",".join("{}={}".format(k, getattr(self, k)) for k in self.__dict__.keys())
    #
    # def __repr__(self):
    #     return ",".join("{}={}".format(k, getattr(self, k)) for k in self.__dict__.keys())+"\n"

    # def to_dict(self):
    #     return dict((k, getattr(self, k)) for k in self.__dict__.keys())
