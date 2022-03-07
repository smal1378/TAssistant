# model.py
# This Is Model, Backend Part Of MVC (Model, View, Controller)
import calendar
import os.path
import time
from typing import Optional, List, Tuple, Dict, Generator, Callable, Any, Union
from pickle import dump, UnpicklingError
from PyQt5.QtCore import QThread
from others.restricted_pickle import loads

VER = 1.0
BETA = False
DATE = 1646333452


class DayStructure:
    time_states = {
        0: ("Can't Join",),
        1: ("Hardly Can",),
        2: ("Okay With It",),
        3: ("Perfect Timing",),
        4: ("Not Set",)
    }
    time_state_colors = {
        0: "#faa",
        1: "#ffa",
        2: "#dfd",
        3: "#afa",
        4: "#bbb"
    }

    def __init__(self, start: int = 8, end: int = 20, step: int = 2,
                 data: Optional[List[Tuple[int, int]]] = None):
        if data:
            raise NotImplemented("Not Implemented Yet")
        else:
            data = []
            for i in range(start, end, step):
                data.append((i, i + step, 4))
        self._data: List[Tuple[int, int, int]] = data

    def get_times(self) -> List[Tuple[int, int, int]]:
        return self._data.copy()

    def get_time(self, index: int) -> Tuple[int, int, int]:
        assert isinstance(index, int), f"Index Must Be Integer: {index}"
        assert 0 <= index < len(self._data), f"Index Out Of Range: {index}"
        return self._data[index]

    def set_time(self, index: int, state: int):
        assert isinstance(index, int), f"Index Must Be Integer: {index}"
        assert isinstance(state, int), f"State Must Be Integer: {state}"
        assert 0 <= index < len(self._data), f"Index Out Of Range: {index}"
        assert state in self.time_states, f"State Not Found: {state}"
        old = self._data[index]
        self._data[index] = (old[0], old[1], state)

    def matches(self, other: "DayStructure") -> bool:
        if len(self._data) != len(other._data):
            return False
        for (start1, end1, state1), (start2, end2, state2) in zip(self._data, other._data):
            if start1 != start2 or end1 != end2:
                return False
        return True


class WeekStructure:
    day_names: Dict[int, Tuple[str]] = {
        0: ('Saturday',),
        1: ('Sunday',),
        2: ('Monday',),
        3: ('Tuesday',),
        4: ('Wednesday',),
        5: ('Thursday',),
        6: ('Friday',)
    }

    def __init__(self, data: Optional[List[DayStructure]] = None):
        if data:
            assert len(data) == 7, f'Data Size Should Be 7 {data}'
            assert all(isinstance(day, DayStructure) for day in data), \
                f"data Contains non-DayStructure: {data}"
        else:
            data = [DayStructure() for _ in range(7)]
        self._data: List[DayStructure] = data

    def get_day(self, day_number: int) -> DayStructure:
        assert isinstance(day_number, int), f"day_number Is Not Integer {day_number}"
        assert 0 <= day_number <= 7, f"day_number Out Of Range {day_number}"
        return self._data[day_number]

    def __iter__(self) -> Generator[DayStructure, None, None]:
        for i in range(7):
            yield self.get_day(i)

    def matches(self, other: "WeekStructure") -> bool:
        for day1, day2 in zip(self._data, other._data):
            if not day1.matches(day2):
                return False
        return True


class Student:
    importance_states = {
        0: ("Not At All",),
        1: ("I'll Try Too",),
        2: ("Mostly All Of Them",),
        3: ("Presenter",)
    }

    def __init__(self, name: str, _id: int, github: str = ""):
        self.name = name
        self.id = _id
        self.github = github
        self.week = WeekStructure()
        self.importance = 1

    def set_importance(self, new: int):
        assert new in self.importance_states, f"New State Not Found: {new}"
        self.importance = new


class StudentManager:
    def __init__(self, name: str = ""):
        self.name = name
        self._students: Dict[int, Student] = {}  # _id: Student

    def add_student(self, name: str = "", _id: int = 0, github: str = "",
                    student: Optional[Student] = None) -> Student:
        if student is not None:
            self._students[student.id] = student
        else:
            assert isinstance(name, str), f"name Is Not str: {name}"
            assert name, f"name Is Empty: {name}"
            assert isinstance(_id, int), f"_id Is Not int: {_id}"
            assert isinstance(github, str), f"github Is Not str: {github}"
            stu = Student(name, _id, github)
            self._students[_id] = stu
            return stu

    def get_student(self, _id) -> Optional[Student]:
        return self._students.get(_id)

    def get_students(self):
        yield from self._students.values()

    def extend(self, other: "StudentManager", match: Optional[WeekStructure] = None):
        assert isinstance(other, StudentManager), f"Other Is Not StudentManager: {other}"
        assert not match or isinstance(match, WeekStructure), f"Match Is Not WeekStructure: {match}"
        for key, value in other._students.items():
            if match and not match.matches(value.week):
                continue
            self._students[key] = value


class PlotResult:
    _id = 1000

    def __init__(self, states: Dict[int, str], time_data: List[Tuple[int, int]], ):
        self.time_states = states
        tim = time.localtime()
        self.note = f"My Scanner {tim.tm_hour}:{tim.tm_min}"
        self.id = PlotResult._id
        PlotResult._id += 1
        self.daily_time_data = time_data
        self._data: List[Optional[List[Dict]]] = \
            [[{state: 0 for state in states.keys()} for _ in range(len(time_data))] for _ in range(7)]
        self._data = []
        for _ in range(7):
            ls = []
            self._data.append(ls)
            for _ in range(len(time_data)):
                di = {state: 0 for state in states}
                di['is_off'] = False
                ls.append(di)

    def increase(self, day: int, index: int, state: int, amount: int):
        self._data[day][index][state] += amount

    def set_off(self, day: int, index: int, flag: bool = True):
        self._data[day][index]['is_off'] = flag

    def get(self, day: int, index: int):
        d = self._data[day][index].copy()
        del d['is_off']
        return d

    def get_table(self):
        return self._data  # can't copy this, due to internal mutable objects :)

    def is_on(self, day: int, index: int) -> bool:
        return not self._data[day][index]['is_off']

    def export(self, filename: str, callback: Callable = None):
        assert isinstance(filename, str), f"filename Is Not str: {filename}"
        assert os.path.exists(os.path.dirname(filename)), f"No Such Directory: {filename}"
        Export(filename, self, callback)


class Scanner:
    def __init__(self, name: str = ""):
        self.name = name
        self._manager = StudentManager()

    def add_student(self, name: str = "", _id: int = 0,
                    student: Optional[Student] = None):
        if student is not None:
            assert isinstance(student, Student), f"student Is Not Student: {student}"
        else:
            assert isinstance(name, str), f"name Is Not str: {name}"
            assert name, f"name Is Empty: {name}"
            assert isinstance(_id, int), f"_id Is Not int: {_id}"
        self._manager.add_student(name=name, _id=_id, student=student)

    def add_student_manager(self, manager: StudentManager):
        nex = next(self._manager.get_students(), None)
        if nex:
            nex = nex.week
        self._manager.extend(manager, match=nex)

    def get_students(self):
        yield from self._manager.get_students()

    def get_student(self, _id: int):
        return self._manager.get_student(_id)

    def get_student_manager(self) -> StudentManager:
        return self._manager

    def all_matches(self) -> Tuple[bool, str, str]:
        gen = self._manager.get_students()
        current: Student = next(gen, None)
        if not current:
            return False, "N/A", "N/A"
        for student in gen:
            if not current.week.matches(student.week):
                return False, current.name, student.name
        return True, "", ""

    def plot_week(self,
                  nones_state: Optional[List] = None,
                  presenters_state: Optional[List] = None,
                  ) -> PlotResult:
        flag, name1, name2 = self.all_matches()
        assert flag, f"Not Match {name1} and {name2}"
        if not nones_state:
            nones_state = []
        if not presenters_state:
            presenters_state = []
        daily_time = [(start, end) for start, end, _ in next(self.get_students()).week.get_day(0).get_times()]
        # importance_states = {key: value for key, value in next(self.get_students()).importance_states.items()}
        time_states = next(self.get_students()).week.get_day(0).time_states
        # print(f"Nones State: {nones_state}")
        # print(f"Presenters State: {presenters_state}")
        # print(f"Daily: {daily_time}")
        # print(f"Importance States: {importance_states}")
        # print(f"Time States: {time_states}")
        plot = PlotResult(time_states, daily_time)
        for student in self.get_students():
            if student.importance in nones_state:
                continue
            day_index = 0
            for day in student.week:
                time_index = 0
                for start, end, state in day.get_times():
                    if student.importance in presenters_state and state == 0:
                        plot.set_off(day_index, day_index)
                    plot.increase(day_index, time_index, state, 1)
                    time_index += 1
                day_index += 1
        mini = 50
        for day in range(7):
            for index, _ in enumerate(daily_time):
                if plot.get(day, index)[0] < mini:
                    mini = plot.get(day, index)[0]
        for day in range(7):
            for index, _ in enumerate(daily_time):
                if plot.get(day, index)[0] > mini:
                    plot.set_off(day, index)
        return plot


class Core:
    def __init__(self):
        self._managers: Dict[str, StudentManager] = {}  # name: StudentManager
        self._scans: Dict[str, Scanner] = {}  # name: Scanner
        self._scan_results: List[PlotResult] = []
        self._student: Optional[Student] = None

    def set_student(self, name: str, _id: int, github: str = "") -> Student:
        assert self._student is None, f"Student Already Exists: {self._student.name}"
        self._student = Student(name, _id, github)
        return self._student

    def get_student(self) -> Optional[Student]:
        return self._student

    def remove_student(self):
        # This Might Cause Loss Of WeeklyReport,
        # You'll probably be thinking why I implemented it? no idea.
        raise NotImplemented("This Might Cause Loss Of Data")
        # self._student = None

    def add_manager(self, name: str):
        assert isinstance(name, str), f"name Is Not str: {name}"
        assert name not in self._managers, f"name Exists: {name}"
        self._managers[name] = StudentManager(name)

    def get_manager(self, name: str):
        assert isinstance(name, str), f"name Is Not str: {name}"
        assert name in self._managers, f"name Doesn't Exists: {name}"
        return self._managers[name]

    def del_manager(self, name: str):
        assert isinstance(name, str), f"name Is Not str: {name}"
        assert name in self._managers, f"name Doesn't Exists: {name}"
        del self._managers[name]

    def get_managers(self) -> Generator[Tuple[str, StudentManager], None, None]:
        yield from self._managers.items()

    def export_manager(self, name: str, filename: str, callback: Callable[[], None] = None):
        assert isinstance(name, str), f"name Is Not str: {name}"
        assert isinstance(filename, str), f"filename Is Not str: {filename}"
        assert os.path.exists(os.path.dirname(filename)), f"No Such Directory: {filename}"
        assert name in self._managers, f"name Does Not Exists: {name}"
        Export(filename, self._managers[name], callback)

    def is_manager(self, name: str):
        return name in self._managers

    def save_self(self, callback: Callable[[], None] = None):
        Export('data.pkl', self, callback)

    def save_as(self, filename: str, callback: Callable[[], None] = None):
        assert isinstance(filename, str), f"filename Should Be str: {filename}"
        assert os.path.exists(os.path.dirname(filename)), f"Directory Does Not Exists: {filename}"
        Export(filename, self, callback)

    def add_scan(self, name: str, *args: Union[Student, StudentManager, Scanner],
                 include_self: bool = False) -> Scanner:
        assert isinstance(name, str), f"name Is Not str: {name}"
        assert name not in self._scans, f"name Exists: {name}"
        scan = Scanner(name)
        if include_self and self._student:
            scan.add_student(student=self._student)
        for element in args:
            if isinstance(element, Student):
                scan.add_student(student=element)
            elif isinstance(element, StudentManager):
                scan.add_student_manager(element)
            elif isinstance(element, Scanner):
                scan.add_student_manager(element.get_student_manager())
        self._scans[name] = scan
        return scan

    def get_scan(self, name: str) -> Optional[Scanner]:
        return self._scans.get(name, None)

    def export_scan(self, name: str, filename: str, callback: Callable[[], None] = None):
        assert isinstance(name, str), f"name Is Not str: {name}"
        assert isinstance(filename, str), f"filename Is Not str {filename}"
        assert os.path.exists(os.path.dirname(filename)), f"Directory Does Not Exists: {filename}"
        assert name in self._scans, f"name Does Not Exists: {name}"
        Export(filename, self._scans[name], callback)

    def is_scan(self, name: str):
        return name in self._scans

    def add_scan_result(self, plot: PlotResult):
        assert isinstance(plot, PlotResult), f"plot Is Not PlotResult: {plot}"
        self._scan_results.append(plot)

    def remove_scan_result(self, plot: PlotResult = None, _id: int = None):
        assert plot is not None or _id is not None, "No Argument Passed To Function"
        assert not plot or isinstance(plot, PlotResult), f"plot Is Not PlotResult: {plot}"
        assert _id is None or isinstance(_id, int), f"_id Is Not int: {_id}"
        if plot:
            self._scan_results.remove(plot)
        else:
            for index, element in enumerate(self._scan_results):
                if element.id == _id:
                    self._scan_results.pop(index)

    def clear_scan_results(self):
        self._scan_results.clear()

    def get_scan_results(self) -> List[PlotResult]:
        return self._scan_results.copy()

    def export_weekly_report(self, filename: str, callback: Callable[[], None] = None):
        assert self._student is not None, "Student Is Not Defined"
        assert isinstance(filename, str), f"filename Is Not str: {filename}"
        assert os.path.exists(os.path.dirname(filename)), f"Directory Does Not Exists: {filename}"
        Export(filename, self._student, callback)

    def import_students(self, filename: str, target: Union[StudentManager, Scanner],
                        callback: Callable[[int], None] = None):
        """
        Loads Students From File, Scanner, StudentManager, Core or Student Export File.
        :param filename: filename or full address to file
        :param target: where to append loaded students, StudentManager or Scanner object
        :param callback: calls this function whenever finishes with error code, 0 means success, 1 file corrupt
        :return: None
        """
        assert isinstance(filename, str), f"filename Is Not str: {filename}"
        assert os.path.exists(filename), f"File Does Not Exists: {filename}"
        assert isinstance(target, (StudentManager, Scanner)), \
            f"target Should Be StudentManager Or Scanner: {target}"
        try:
            Import(filename, lambda d: self._import_students_helper(d, callback, target))
        except UnpicklingError:
            if callback:
                callback(1)

    @staticmethod
    def _import_students_helper(data, callback, target: Union[StudentManager, Scanner]):
        if not isinstance(data, (Student, StudentManager, Core, Scanner)):
            if callback:
                callback(1)
            return
        if isinstance(target, Scanner):
            target = target.get_student_manager()
        if isinstance(data, Student):
            target.add_student(student=data)
        elif isinstance(data, StudentManager):
            target.extend(data)
        elif isinstance(data, Scanner):
            target.extend(data.get_student_manager())
        elif isinstance(data, Core):
            core: Core = data  # Debug Purposes
            if core.get_student():
                target.add_student(student=core.get_student())
            for _, manager in core.get_managers():
                target.extend(manager)
        else:
            callback(1)
            print(f"What?: {data}")
            return
        callback(0)

    @staticmethod
    def get_about():
        d = time.localtime(DATE)
        month = calendar.month_name[d.tm_mon]
        year = d.tm_year
        return f"Teacher Assistant's Assistant Ver{VER}<br>" \
               f"Author: Esmail Mahjoor<br>" \
               f"Date: {month} {year}<br>" \
               f"Telegram: @<a href='https://t.me/smal1378'>smal1378</a>"

    def open_project(self, filename: str,
                     callback: Callable[[int, Optional["Core"]], None]) -> None:
        """
        load core object and pass it to callback, that has been saved with save_self
        errors: 0: successful, 1: file not found, 2: file corrupted, 3: file is not Core
        :param filename: filename to open project from
        :param callback: callable object, it'll be called with a tuple containing error code and core object
        :return: None
        """
        assert isinstance(filename, str), f"filename Should Is Not str: {filename}"
        if not os.path.exists(filename):
            callback(1, None)
        try:
            Import(filename, lambda data: self._open_project_helper(data, callback))
        except UnpicklingError:
            callback(2, None)

    @staticmethod
    def _open_project_helper(data, callback):
        if isinstance(data, Core):
            callback(0, data)
        else:
            callback(3, None)

    def get_scans(self) -> Generator[Scanner, None, None]:
        yield from self._scans.values()

    def del_scan(self, name: str):
        assert isinstance(name, str), f"name Is Not str: {name}"
        assert name in self._scans, f"Scan Does Not Exists: {name}"
        del self._scans[name]


class Export(QThread):
    def __init__(self, filename: str, obj=None, callback: Callable[[], None] = None):
        assert obj is not None, f"obj Is None: {obj}"
        super(Export, self).__init__()
        self.filename = filename
        self.obj = obj
        self.callback = callback
        self.run()  # Fixme: user self.start() instead to run it in it's own thread!

    def run(self) -> None:
        with open(self.filename, "wb") as file:
            dump(self.obj, file)
        if self.callback:
            self.callback()


class Import(QThread):
    def __init__(self, filename: str, callback: Callable[[Any], None]):
        super(Import, self).__init__()
        self.filename = filename
        self.callback = callback
        self.run()  # Fixme: use self.start() to run this on it's own thread

    def run(self):
        with open(self.filename, "rb") as file:
            self.callback(loads(file.read()))  # Fixme: it's better not to use file.read()
