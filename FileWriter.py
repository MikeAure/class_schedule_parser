from icalendar import Calendar, Event, vText, Alarm
from datetime import datetime, timedelta
class FileWriter():
    def __init__(self, schedule:list):
        self.whole_schedule = schedule

    def write_file(self, format_info="ics"):
        if format_info == "ics":
            self.write_ics()
        elif format_info == "json":
            self.write_json()

    def write_ics(self):
        cal = Calendar()
        cal.add('prodid', '-//Whitetree//whitetree.top//CN')
        cal.add('version', '2.0')
        cal.add('X-WR-CALNAME', {datetime.today()})
        cal.add('X-APPLE-CALENDAR-COLOR', '#ff9500')
        cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')

        for week_schedule in self.whole_schedule:
            for week_day in week_schedule.values():
                for lesson in week_day.values():
                    class_info = lesson["class_detail"]
                    event = Event()
                    event.add("summary", class_info["class_name"])
                    event.add("dtstart", lesson["start_time"])
                    event.add('dtend', lesson["end_time"])
                    event.add('DESCRIPTION',
                              '授课教师：' + class_info["teacher_name"]+"\n" +
                              '课时：' + class_info["total_periods"] + "\n" +
                              '学分：' + class_info["score"])
                    event['location'] = vText(class_info["location"])
                    alarm = Alarm()
                    alarm.add('ACTION', 'DISPLAY')
                    alarm.add('TRIGGER', timedelta(minutes=-10))
                    alarm.add('DECRIPTION', '上课提醒')
                    event.add_component(alarm)
                    cal.add_component(event)
        with open("schedule.ics", "wb") as f:
            f.write(cal.to_ical())


    def write_json(self):
        return