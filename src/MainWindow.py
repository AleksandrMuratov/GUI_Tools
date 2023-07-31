from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import pyqtSlot
from MainMenu import MainMenu
import Recipe
import Stat


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Tools')
        main_menu = MainMenu(parent=self)
        self.setMenuBar(main_menu)

        main_menu.mode_recipe_request.connect(self.mode_recipe_on)
        main_menu.mode_stat_request.connect(self.mode_stat_on)

        main_menu.about_qt.triggered.connect(self.about_qt)
        main_menu.about.triggered.connect(self.about)

    @pyqtSlot()
    def mode_recipe_on(self):
        old = self.centralWidget()
        v = Recipe.View(parent=self)
        self.setCentralWidget(v)
        self.menuBar().set_mode_recipe(v)
        if old is not None:
            old.deleteLater()

    @pyqtSlot()
    def mode_stat_on(self):
        old = self.centralWidget()
        v = Stat.View(parent=self)
        self.setCentralWidget(v)
        self.menuBar().set_mode_stat(v)
        if old is not None:
            old.deleteLater()

    @pyqtSlot()
    def about(self):
        title = 'Управление рецептами и выгрузка статистики'
        text = 'Программа для сохранения,\nредактирования и удаления рецептов\nи выгрузки статистики'
        QMessageBox.about(self, title, text)

    @pyqtSlot()
    def about_qt(self):
        QMessageBox.aboutQt(self, 'Управление рецептами')