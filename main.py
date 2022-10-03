from ScheduleParser import ScheduleParser
from FileWriter import FileWriter
import sys

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    file_path = sys.argv[1]
    sch_parser = ScheduleParser()
    try:
        sch_parser.read_schedule_file(file_path)
    except FileNotFoundError:
        print("Please check the file name and file path")


    sch_parser.get_class_list()
    sch_parser.init_start_day()
    sch_parser.retrieve_schedule()
    whole_schdule = sch_parser.update_schedule_date()
    ics_writer = FileWriter(whole_schdule)
    ics_writer.write_file()

