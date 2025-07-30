from importlib import resources
from typing import Tuple

from PyQt5.QtCore import QThread, pyqtSlot, QSettings
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QStatusBar

from comp.models import CenterData
from comp.ui.config_run_tab import ConfigRunTab
from comp.ui.data_load_tab import DataLoadTab
from comp.ui.results_tab import ResultsTab
from comp.ui.styles import STYLESHEET
from comp.ui.worker import SolverWorker


class MainWindow(QMainWindow):
    """
    The main application window.

    Hosts tabs for different operations (data load, config/run, results).
    Manages solver worker threads and persists window geometry.
    """

    def __init__(self):
        """Initializes the MainWindow, setting up UI and QSettings."""

        super().__init__()

        self.settings = QSettings("megistone", "COMP-UI")
        self.data_load_tab = None
        self.config_run_tab = None
        self.results_tab = None
        self.status_bar = None
        self.tab_widget = None
        self.center_data = None
        self.solver_instance = None
        self.results_text_data = None
        self.results_dict_data = None
        self.solver_thread = None
        self.solver_worker = None
        self.init_ui()

    def init_ui(self, resolution: Tuple[int, int] = (1280, 720)):
        """
        Initializes the main window’s UI components.

        Sets up title, icon, size, stylesheet, tab widget, tabs, and status bar.
        Connects tab signals.

        :param resolution: Default window size (width, height).
        """

        self.setWindowTitle("УЗГОДЖЕНЕ ПЛАНУВАННЯ В ДВОРІВНЕВИХ ОРГАНІЗАЦІЙНО-ВИРОБНИЧИХ СИСТЕМАХ")

        try:
            icon_bytes = resources.read_binary("comp.media", "COMP.ico")
            pixmap = QPixmap()
            if pixmap.loadFromData(icon_bytes):
                self.setWindowIcon(QIcon(pixmap))
            else:
                print("Warning: Failed to load icon data into QPixmap for \"COMP.ico\". Using default icon.")
        except FileNotFoundError:
            print("Warning: Icon \"COMP.ico\" not found in package \"comp.media\". Using default icon.")
        except Exception as e:
            print(f"Warning: Could not load icon \"COMP.ico\" due to: {e}. Using default icon.")

        self.setMinimumSize(*resolution)

        if geometry := self.settings.value("geometry"):
            self.restoreGeometry(geometry)
        else:
            self.setGeometry(100, 100, *resolution)

        self.setStyleSheet(STYLESHEET)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.tabBar().setExpanding(True)
        self.setCentralWidget(self.tab_widget)

        self.data_load_tab = DataLoadTab()
        self.config_run_tab = ConfigRunTab()
        self.results_tab = ResultsTab()

        self.tab_widget.addTab(self.data_load_tab, "Завантаження даних")
        self.tab_widget.addTab(self.config_run_tab, "Налаштування та Розрахунок")
        self.tab_widget.addTab(self.results_tab, "Перегляд результатів")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово до роботи.")

        self.data_load_tab.data_loaded.connect(self.on_data_loaded)
        self.config_run_tab.run_calculation_requested.connect(self.run_calculation)

        self.data_load_tab.status_updated.connect(self.status_bar.showMessage)
        self.config_run_tab.status_updated.connect(self.status_bar.showMessage)
        self.results_tab.status_updated.connect(self.status_bar.showMessage)

    @pyqtSlot(object)
    def on_data_loaded(self, center_data: CenterData):
        """
        Handles new data loaded from DataLoadTab.

        Updates internal data, resets solver/results, and updates UI tabs.
        Switch to ConfigRunTab if data is valid.

        :param center_data: Loaded `CenterData` or None on failure.
        """

        self.center_data = center_data
        self.solver_instance = None
        self.results_text_data = None
        self.results_dict_data = None

        self.config_run_tab.update_config_display(center_data)
        self.results_tab.clear_results()
        if center_data:
            self.tab_widget.setCurrentWidget(self.config_run_tab)

    @pyqtSlot(object)
    def run_calculation(self, modified_center_data: CenterData):
        """
        Starts a new calculation using SolverWorker in a QThread.

        Prevents multiple concurrent calculations.
        Passes `modified_center_data` to the worker.

        :param modified_center_data: `CenterData` with user configurations.
        """

        if self.solver_thread and self.solver_thread.isRunning():
            QMessageBox.information(self, "Розрахунок триває", "Будь ласка, зачекайте завершення поточного розрахунку.")
            return

        self.center_data = modified_center_data
        self.solver_thread = QThread()
        self.solver_worker = SolverWorker(self.center_data)
        self.solver_worker.moveToThread(self.solver_thread)

        self.solver_worker.finished.connect(self.on_calculation_finished)
        self.solver_worker.error.connect(self.on_calculation_error)
        self.solver_worker.progress.connect(self.config_run_tab.set_progress)

        self.solver_thread.started.connect(self.solver_worker.run)  # type: ignore
        self.solver_thread.finished.connect(self.solver_thread.deleteLater)  # type: ignore
        self.solver_worker.finished.connect(self.solver_thread.quit)
        self.solver_worker.error.connect(self.solver_thread.quit)

        self.solver_thread.start()

    @pyqtSlot(object, str, dict, str)
    def on_calculation_finished(self, solver_instance, results_text, results_dict, status_message):
        """
        Handles successful completion of a calculation from SolverWorker.

        Stores results, updates UI (ConfigRunTab, ResultsTab, status bar),
        and cleans up the solver thread.

        :param solver_instance: The solver instance.
        :param results_text: Formatted textual results.
        :param results_dict: Structured results’ dictionary.
        :param status_message: Message for the status bar.
        """

        self.solver_instance = solver_instance
        self.results_text_data = results_text
        self.results_dict_data = results_dict

        self.config_run_tab.calculation_finished(True)
        self.results_tab.display_results(results_text, solver_instance)
        self.status_bar.showMessage(status_message)
        self.tab_widget.setCurrentWidget(self.results_tab)

        if self.solver_thread:
            self.solver_thread.quit()
            self.solver_thread.wait()
            self.solver_thread = None
        self.solver_worker = None

    @pyqtSlot(str)
    def on_calculation_error(self, error_message):
        """
        Handles errors reported by the SolverWorker.

        Shows an error message, updates UI (ConfigRunTab, status bar),
        and cleans up the solver thread.

        :param error_message: Error message from the worker.
        """

        QMessageBox.critical(self, "Помилка розрахунку", error_message)
        self.config_run_tab.calculation_finished(False)
        self.status_bar.showMessage(f"Помилка: {error_message}")
        if self.solver_thread:
            self.solver_thread.quit()
            self.solver_thread.wait()
            self.solver_thread = None
        self.solver_worker = None

    def closeEvent(self, event, wait_time: int = 5000):
        """
        Handles the window close event.

        Prompts user if calculation is running.
        Manage solver thread shutdown.
        Saves window geometry.

        :param event: The QCloseEvent.
        :param wait_time: Max time (ms) to wait for thread graceful shutdown.
        """

        if self.solver_thread and self.solver_thread.isRunning():
            reply = QMessageBox.question(self, "Вихід", "Розрахунок ще триває. Ви впевнені, що хочете вийти?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.solver_worker and hasattr(self.solver_worker, "stop"):
                    self.solver_worker.stop()
                if self.solver_thread:
                    self.solver_thread.quit()
                    if not self.solver_thread.wait(wait_time):
                        print("Solver thread did not quit in time, forcing termination.")
                        self.solver_thread.terminate()
                        self.solver_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            self.settings.setValue("geometry", self.saveGeometry())
            event.accept()
