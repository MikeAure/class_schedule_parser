import copy
import datetime
import json
import re
import pytz
import bs4

from Class import Class


class ScheduleParser:
    def __init__(self):
        self.one_day = datetime.timedelta(days=1)
        self.original_html = None
        self.extracted_schedule_detail = None
        self.extracted_class_detail = None
        self.class_list = []
        self.schedule_detail = {}
        self.total_week_number = 20
        self.whole_schedule = None
        self.start_date = datetime.date(2022, 9, 1)
        self.cl_start = {'1-2': datetime.time(8, 10, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                         '1-4': datetime.time(8, 10, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                         '3-4': datetime.time(10, 15, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                         '5-6': datetime.time(14, 30, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                         '5-8': datetime.time(14, 30, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                         '7-8': datetime.time(16, 25, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                         '9-10': datetime.time(19, 10, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                         '9-11': datetime.time(19, 10, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai'))
                         }

        self.cl_end = {'1-2': datetime.time(9, 45, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                       '1-4': datetime.time(11, 50, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                       '3-4': datetime.time(11, 50, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                       '5-6': datetime.time(16, 5, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                       '5-8': datetime.time(18, 0, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                       '7-8': datetime.time(18, 0, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                       '9-10': datetime.time(20, 45, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')),
                       '9-11': datetime.time(21, 35, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai'))
                       }

    def read_schedule_file(self, file_path: str):
        if not (file_path.endswith("html") or file_path.endswith("htm")):
            raise Exception("Illegal file path")

        with open(file_path, "r", encoding="utf-8") as fp:
            self.original_html = bs4.BeautifulSoup(fp, 'html.parser')
        self.original_html.prettify()
        # tables = self.original_html.body.contents
        for table in self.original_html.body.children:
            if isinstance(table, bs4.Tag) and table.has_attr("class"):
                if table["class"] == ["tab1"]:
                    self.extracted_schedule_detail = table.tbody.find_all("tr")[2:]
                    self.total_week_number = len(self.extracted_schedule_detail)
                if table["class"] == ["tab2"]:
                    self.extracted_class_detail = table.find_all("td", recursive=True)
        ex_temp = []
        for class_info in self.extracted_class_detail:
            if class_info.contents != [] and isinstance(class_info, bs4.Tag):
                ex_temp.append(class_info)
        self.extracted_class_detail = ex_temp

    def get_class_list(self):

        class_list = []

        basic_info_re = re.compile(r"\((?P<class_name_part_abbr>\w+)\)\s+"
                                   r"(?P<class_name>\w+[\（\d\）]*)\[\w+\]\s?"
                                   r"学分\[(?P<class_score>\d+\.?\d*)\]")

        detail_info_re = re.compile(r"(?P<class_code>\w+)"
                                    r"\[(?P<class_type>\w?)\]\s{1,3}"
                                    r"时\[(?P<class_total_periods>\d+)\]\s?"
                                    r"师\[(?P<teacher_name>[\w\,]+)\]\s?"
                                    r"室\[(?P<location>[\w\,]+)\]")

        for item in self.extracted_class_detail:
            if isinstance(item, bs4.Tag):
                basic_info = item.b.extract().text
                detail_info_list = item.get_text(strip=True, separator="\n").splitlines()
                basic_info_re_res = re.match(basic_info_re, basic_info)
                class_name_part_abbr = basic_info_re_res.group("class_name_part_abbr")
                class_name = basic_info_re_res.group("class_name")
                class_score = basic_info_re_res.group("class_score")
                for detail_info in detail_info_list:
                    detail_info_re_res = re.match(detail_info_re, detail_info)
                    class_code = detail_info_re_res.group("class_code")
                    class_type = detail_info_re_res.group("class_type")
                    class_total_periods = detail_info_re_res.group("class_total_periods")
                    teacher_name = detail_info_re_res.group("teacher_name").strip(",")
                    location = detail_info_re_res.group("location")
                    class_abbr = class_name_part_abbr + class_code

                    class_item = Class(class_abbr, class_name, location, teacher_name,
                                       score=class_score, total_periods=class_total_periods, class_type=class_type)
                    class_list.append(class_item)

        self.class_list = class_list

    def init_start_day(self):

        first_week = self.extracted_schedule_detail[0]
        for day in first_week:
            if isinstance(day, bs4.Tag):
                date_string = day.text
                break
        try:
            date_re = re.match(r"(\d+)周(\d+)/(\d+)-(\d+/\d+)", date_string)
        except Exception as err:
            print(err)
            print("Initialize start date failed")

        start_month = int(date_re.group(2))
        start_day = int(date_re.group(3))
        self.start_date = datetime.date.today().replace(month=start_month, day=start_day)

    def abbr_search(self, abbr):

        for class_item in self.class_list:
            if class_item["class_abbr"] == abbr:
                res = class_item
                return res
        return None

    def retrieve_schedule(self):
        class_counter = class_duration = 0
        search_res = None
        whole_schedule = []
        weekly_schedule = {}
        start_date = copy.deepcopy(self.start_date)

        for week_item in self.extracted_schedule_detail:
            weekly_schedule.clear()
            day_schedule = {}

            total_counter = 1
            week_day = 1

            for daily_item in week_item:

                newest_weekday = total_counter // 12 + 1
                if newest_weekday != week_day:
                    start_date += self.one_day
                    week_day = newest_weekday
                    day_schedule.clear()

                if not isinstance(daily_item, bs4.Tag):
                    continue
                if daily_item.has_attr("bgcolor"):
                    continue

                if len(daily_item.attrs) == 2:
                    total_counter += 1
                    continue

                if daily_item.has_attr("colspan"):
                    class_duration = int(daily_item["colspan"])
                    abbr = daily_item.contents[0]
                    search_res = self.abbr_search(abbr)
                    class_counter = total_counter % 12
                    total_counter += class_duration

                if search_res is not None:
                    if class_counter == 6 or class_counter == 8 or class_counter == 10:
                        class_counter -= 1
                    location = daily_item.contents[2]
                    search_res["location"] = location
                    class_num = str(class_counter) + "-" + str(class_counter + class_duration - 1)
                    class_info_temp = dict({"start_time": self.cl_start[class_num],
                                            "end_time": self.cl_end[class_num],
                                            "class_detail": search_res})
                    day_schedule.update({class_num: class_info_temp})

                # newest_weekday = total_counter // 14 + 1
                # if newest_weekday != week_day:
                #     week_day = newest_weekday
                #     day_schedule.clear()
                weekly_schedule.update({str(week_day): day_schedule.copy()})

            whole_schedule.append(weekly_schedule.copy())

        self.whole_schedule = whole_schedule
        return self.whole_schedule

    def update_schedule_date(self):
        for week_num in range(len(self.whole_schedule)):
            week_delta = datetime.timedelta(weeks=week_num)
            for weekday, lessons in self.whole_schedule[week_num].items():
                time_delta = week_delta + datetime.timedelta(days=int(weekday)-1)
                if len(lessons) == 0:
                    continue
                for class_info in lessons.values():
                    class_info["start_time"] = datetime.datetime.combine(self.start_date + time_delta,
                                                                         class_info["start_time"])
                    class_info["end_time"] = datetime.datetime.combine(self.start_date + time_delta,
                                                                       class_info["end_time"])

        return self.whole_schedule
