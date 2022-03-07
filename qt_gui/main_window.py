from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from model import Core, VER, StudentManager, Scanner
from qt_gui.about_window import About
from qt_gui.dialogs import AskToSave, ErrorMessage, LineGet, AskYesNo
from qt_gui.plot_window import Plot
from qt_gui.set_stu_window import SetStudent
from qt_gui.student_window import StudentView
from qt_gui.students_window import StudentsList


class MainWindow(QMainWindow):
    def __init__(self, core: Core):
        super(MainWindow, self).__init__()
        self.need_to_save = False
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        self.filename = ''
        self.core = core
        self.setWindowTitle(f"TAssistant V{VER}")
        self.setMinimumSize(1200, 800)
        self.closeEvent = self.proper_exit
        self._initialize_menus()

    def _initialize_menus(self):
        menu = self.menuBar()

        # file
        file = menu.addMenu("&File")
        open_ = file.addAction("&Open Project")
        open_.triggered.connect(self._ac_open)
        open_.setShortcut("Ctrl+O")
        save = file.addAction("&Save Project")
        save.triggered.connect(self._ac_save)
        save.setShortcut("Ctrl+S")
        save_as = file.addAction("Save As..")
        save_as.triggered.connect(self._ac_save_as)
        file.addSeparator()
        _exit = file.addAction("&Exit")
        _exit.triggered.connect(self.proper_exit)

        # self
        self.self_menu = self_ = menu.addMenu("&Self")
        self._reload_self_menu()

        # managers
        self.manager_menu = menu.addMenu("&Manager")
        self._reload_manager_menu()

        # scans
        self.scan_menu = menu.addMenu("S&can")
        self._reload_scan_menu()

        # View
        view = menu.addMenu("&View")
        view.setEnabled(False)

        # Help
        help_ = menu.addMenu("Help")
        about = help_.addAction("About")
        about.triggered.connect(self._ac_about)
        update = help_.addAction("Check For Updates..")
        update.setEnabled(False)

    def _reload_scan_menu(self):
        self.scan_menu.clear()
        for scan in self.core.get_scans():
            menu = self.scan_menu.addMenu(scan.name)
            stu = menu.addAction("Import Students..")
            stu.triggered.connect(lambda x, e=scan: self._ac_import_student_scan(e))
            lst = menu.addAction("List Students")
            lst.triggered.connect(lambda x, e=scan: self._ac_list_student_scan(e))
            scan1 = menu.addAction("Start Scan")
            scan1.triggered.connect(lambda x, e=scan: self._ac_start_scan(e))
            exp = menu.addAction("Export..")
            exp.triggered.connect(lambda x, e=scan: self._ac_export_scan(e))
            del_ = menu.addAction("Delete")
            del_.triggered.connect(lambda x, e=scan: self._ac_del_scan(e))
        self.scan_menu.addSeparator()
        imp = self.scan_menu.addAction("Import Scanner..")
        imp.triggered.connect(self._ac_import_scan)
        imp.setEnabled(False)
        new = self.scan_menu.addAction("New Scanner")
        new.triggered.connect(self._ac_new_scan)

    def _ac_start_scan(self, scan: Scanner):
        matches, name1, name2 = scan.all_matches()
        if matches:
            plot = scan.plot_week([0], [3])
            Plot(self, plot).show()
        else:
            ErrorMessage(self, "Looks Like Students Weekly Schedules Does Not Match.\n"
                               f"Student {name1} and {name2}.").show()

    def _ac_import_scan(self):
        pass

    def _ac_export_scan(self, scan: Scanner):
        dia = QFileDialog(self, "Choose Scan File")
        file = dia.getSaveFileName(directory="my_scanner_export.taascan",
                                   filter="Scanner Export(*.taascan);;All Files(*.*)")[0]
        if file:
            self.core.export_scan(scan.name, file, lambda: print("Exported"))

    def _ac_list_student_scan(self, scan: Scanner):
        stu = StudentsList(self, scan.get_student_manager())
        stu.on_need_to_save.connect(self.set_need_to_save)
        stu.show()

    def _ac_import_student_scan(self, scan: Scanner):
        dia = QFileDialog(self, "Choose Scan File")
        files = dia.getOpenFileNames(filter='Project(*.taaproj);;'
                                            'Weekly Export(*.taaexp);;'
                                            'Manager Export(*.taaman);;'
                                            'Scanner Export(*.taascan);;'
                                            'All Files(*.*)')[0]
        for file in files:
            self.core.import_students(file, scan, (lambda e: self.set_need_to_save() if e == 0
                                      else ErrorMessage(self, f"Error, code: {e}\n"
                                                              f"Filename: {file}").show()))

    def _ac_del_scan(self, scan: Scanner):
        if AskYesNo(None, f"Are You Sure You Want To Delete {scan.name}?").is_yes():
            self.core.del_scan(scan.name)
            self.set_need_to_save()
            self._reload_scan_menu()

    def _ac_new_scan(self):
        line = LineGet(None, "Scanner Name", lambda e: bool(e) and not self.core.is_scan(e))
        line.set_checkbox("self", "Include my weekly schedule", True)
        name = line.get()
        if name:
            self.core.add_scan(name, include_self=line.get_checkbox('self'))
            self.set_need_to_save()
            self._reload_scan_menu()

    def _reload_manager_menu(self):
        menu = self.manager_menu
        menu.clear()
        for name, manager in self.core.get_managers():
            men = menu.addMenu(name)
            add = men.addAction("Add Student")
            add.triggered.connect(lambda t, e=manager: self._ac_manager_add_stu(e))
            lst = men.addAction("List Students")
            lst.triggered.connect(lambda t, e=manager: self._ac_manager_list_stu(e))
            exp = men.addAction("Export..")
            exp.triggered.connect(lambda t, e=manager: self._ac_manager_export(e))
            imp = men.addAction("Import Students..")
            imp.triggered.connect(lambda t, e=manager: self._ac_manager_import(e))
            del_ = men.addAction("Delete")
            del_.triggered.connect(lambda t, e=manager: self._ac_manager_del(e))
        new = menu.addAction("New Student Manager")
        new.triggered.connect(self._ac_new_manager)

    def _ac_manager_del(self, manager: StudentManager):
        if AskYesNo(None, f"Are You Sure You Want To Delete {manager.name}?").is_yes():
            self.core.del_manager(manager.name)
            self.set_need_to_save()
            self._reload_manager_menu()

    def _ac_manager_import(self, manager: StudentManager):
        dia = QFileDialog(self, "Choose Export File:")
        files = dia.getOpenFileNames(filter='Project(*.taaproj);;'
                                            'Weekly Export(*.taaexp);;'
                                            'Manager Export(*.taaman);;'
                                            'Scanner Export(*.taascan);;'
                                            'All Files(*.*)')[0]
        for file in files:
            self.core.import_students(file, manager,
                                      lambda code: ErrorMessage(self, "File Corrupt").show()
                                      if code == 1 else (print("Imported"), self.set_need_to_save()))

    def _ac_manager_export(self, manager: StudentManager):
        dia = QFileDialog(self, "Choose Export File:")
        file = dia.getSaveFileName(filter="Manager Export(*.taaman);;All Files(*.*)")[0]
        if file:
            self.core.export_manager(manager.name, file, lambda: print("Exported"))

    def _ac_manager_list_stu(self, manager: StudentManager):
        stu = StudentsList(self, manager)
        stu.on_need_to_save.connect(self.set_need_to_save)
        stu.show()

    def _ac_manager_add_stu(self, manager: StudentManager):
        stu = SetStudent(self)
        stu.show()
        stu.entered.connect(lambda x, y, z: self._ac_manager_add_stu_helper(x, y, z,
                                                                            stu, manager))

    def _ac_manager_add_stu_helper(self, x, y, z, s, m):
        if not (x and y):
            s.show_error("Both Fields Should Be Filled!")
        elif not y.isnumeric():
            s.show_error("How Does Your Id Contain Letters?")
        elif not 9 <= len(y) <= 10:
            s.show_error("Your Id Should Be 9 Characters!")
        else:
            s.close()
            self.set_need_to_save()
            m.add_student(x, int(y), z)

    def _ac_new_manager(self):
        name = LineGet(None, "Manager Name", self._validator_manager).get()
        if name:
            self.core.add_manager(name)
            self.set_need_to_save()
            self._reload_manager_menu()

    def _validator_manager(self, name: str):
        if not name:
            return False
        if self.core.is_manager(name):
            return False
        return True

    def _reload_self_menu(self):
        self.self_menu.clear()
        stu = self.core.get_student()
        if stu:
            stu_menu = self.self_menu.addMenu(stu.name)
            edit = stu_menu.addAction("Edit")
            edit.triggered.connect(self._ac_edit_stu)
        else:
            set_stu = self.self_menu.addAction("Create Profile")
            set_stu.triggered.connect(self._ac_set_stu)
        weekly = self.self_menu.addAction("Weekly Schedule")
        weekly.triggered.connect(self._ac_weekly)
        export_weekly = self.self_menu.addAction("Export Weekly Schedule")
        export_weekly.triggered.connect(self._ac_weekly_export)
        if not stu:
            weekly.setEnabled(False)
            export_weekly.setEnabled(False)

    def proper_exit(self, t=None):
        # first check if self.need_to_save flag is False,
        # Ask to save then call QApplication.quit
        if t:
            t.ignore()
        if self.need_to_save:
            AskToSave(self, lambda: (QApplication.quit() if self.save() else None),
                      lambda: QApplication.quit()).show()
        else:
            QApplication.quit()

    def _ac_open(self):
        if self.need_to_save:
            flag = set()
            x = AskToSave(self, lambda: (flag.add('no'), x.close() if self.save() else 0),
                          lambda: (flag.add('no'), x.close()))
            x.exec()
            if "no" not in flag:
                print('skipped')
                return
        ex = QFileDialog(self, "Choose .taaproj file:")
        es = ex.getOpenFileName(filter="Project(*.taaproj);;All Files(*.*)")[0]
        if es:
            self.core.open_project(es, lambda e, c: self._ac_open_helper(e, c, es))

    def _ac_open_helper(self, error, core, filename):
        if error == 0:
            self.filename = filename
            self.core = core
            self.reload()
        else:  # Todo: support all errors
            ErrorMessage(self, f"Error loading project: {error}").show()

    def _ac_save(self):
        if not self.filename:
            fi = QFileDialog()
            self.filename = fi.getSaveFileName(self, "Save Project To:",
                                               filter="Project(*.taaproj);;All Files(*.*)")[0]

        if self.filename:
            self.core.save_as(self.filename, lambda: print("saved"))
            self.need_to_save = False
            return True
        return False
    save = _ac_save

    def _ac_save_as(self):
        fi = QFileDialog()
        x = fi.getSaveFileName(self, "Save Project To:",
                               filter="Project(*.taaproj);;All Files(*.*)")[0]

        if x:
            self.core.save_as(self.filename, lambda: print("saved"))
            self.filename = x

    def _ac_edit_stu(self):
        stu = self.core.get_student()
        set_stu = SetStudent(self, stu.name, str(stu.id), stu.github)
        set_stu.entered.connect(lambda name, id_, github, e=set_stu:
                                self._slot_set_stu(name, id_, github, set_stu))
        set_stu.show_error("Note: This Might Need Restarting The App"
                           " Or Some Parts Of App Never Update Themselves.")
        set_stu.show()

    def _ac_set_stu(self):
        set_stu = SetStudent(self)
        set_stu.entered.connect(lambda name, id_, github, e=set_stu:
                                self._slot_set_stu(name, id_, github, set_stu))
        set_stu.show()

    def _ac_about(self):
        About(self, self.core.get_about()).show()

    def _ac_weekly(self):
        stu = StudentView(self, self.core.get_student(), edit=True)
        stu.on_need_to_save.connect(self.set_need_to_save)
        stu.show()

    def _ac_weekly_export(self):
        dia = QFileDialog(self, "Save Export Weekly Schedule Report..")
        filename = dia.getSaveFileName(filter="TAA Export(*.taaexp);;All Files(*.*)")[0]
        if filename:
            self.core.export_weekly_report(filename, lambda: print('exported'))

    def _slot_set_stu(self, new_name: str, new_id: str, github: str, set_stu: SetStudent):
        # This slot is used for both, create profile and edit profile.
        if not (new_id and new_name):
            set_stu.show_error("Both Fields Should Be Filled!")
        elif not new_id.isnumeric():
            set_stu.show_error("How Does Your Id Contain Letters?")
        elif not 9 <= len(new_id) <= 10:
            set_stu.show_error("Your Id Should Be 9 or 10 Characters!")
        else:
            set_stu.close()
            self.set_need_to_save()
            stu = self.core.get_student()
            if stu:
                stu.name = new_name
                stu.id = int(new_id)
                stu.github = github
            else:
                self.core.set_student(new_name, int(new_id), github)
            self._reload_self_menu()

    def set_need_to_save(self):
        self.need_to_save = True

    def reload(self):
        self._reload_self_menu()
        self._reload_manager_menu()
        self._reload_scan_menu()
