from contextlib import redirect_stdout
from io import StringIO

from PyQt5.QtCore import QObject, pyqtSignal

from comp.models import CenterData
from comp.solvers import new_center_solver


class SolverWorker(QObject):
    """
    QObject worker for background solver calculations.

    Emits `finished`, `error`, and `progress` signals.
    Supports a `stop()` method for attempted early termination.
    """

    finished = pyqtSignal(object, str, dict, str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, center_data: CenterData):
        """
        Initializes the SolverWorker.

        :param center_data: `CenterData` for the solver.
        """

        super().__init__()

        self.center_data = center_data
        self.solver = None
        self._is_running = True

    def run(self):
        """
        Executes the solver process: init, coordinate, get results.

        Checks `_is_running` for early termination. Emits `finished` or `error`.
        """

        try:
            self.progress.emit(10)  # type: ignore
            if not self._is_running: return

            if not self.center_data:
                self.error.emit("Дані центру не завантажені.")  # type: ignore
                return

            if not self._is_running: return
            self.solver = new_center_solver(self.center_data)
            self.progress.emit(30)  # type: ignore

            if not self._is_running: return
            self.solver.coordinate()
            self.progress.emit(70)  # type: ignore

            if not self._is_running: return
            f = StringIO()
            with redirect_stdout(f):
                self.solver.print_results()
            results_text = f.getvalue()
            self.progress.emit(90)  # type: ignore

            if not self._is_running: return
            results_dict = self.solver.get_results_dict()
            self.progress.emit(100)  # type: ignore
            if self._is_running:
                self.finished.emit(self.solver, results_text, results_dict,  # type: ignore
                                   "Розрахунок завершено успішно.")
        except Exception as e:
            if self._is_running:
                self.error.emit(f"Помилка під час розрахунку: {str(e)}")  # type: ignore
        finally:
            self._is_running = False

    def stop(self):
        """Signals the worker to stop by setting `_is_running` to False."""

        self._is_running = False
