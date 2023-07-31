from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QActionGroup
from PyQt6.QtCore import pyqtSlot, pyqtSignal

class MainMenu(QMenuBar):

    mode_recipe_request = pyqtSignal()
    mode_stat_request = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        recipe_menu = self.addMenu('Рецепт')
        self.__recipe_menu_action = recipe_menu.menuAction()
        self.__recipe_add = recipe_menu.addAction('Добавить')
        self.__recipe_edit = recipe_menu.addAction('Редактировать')
        self.__recipe_delete = recipe_menu.addAction('Удалить')
        self.__recipe_select = recipe_menu.addAction('Выбрать')

        stat_menu = self.addMenu('Статистика')
        self.__stat_menu_action = stat_menu.menuAction()
        self.__stat_request = stat_menu.addAction('Загрузить')
        self.__stat_print = stat_menu.addAction('Распечатать')
        self.__stat_print_view = stat_menu.addAction('Предварительный просмотр')

        stat_total = self.addMenu('Общая статистика')
        self.__stat_total_action = stat_total.menuAction()
        self.__stat_total_run = stat_total.addAction('Включить')

        stat_recipe = self.addMenu('Сводка по рецептам')
        self.__stat_recipe_action = stat_recipe.menuAction()
        self.__stat_recipe_run = stat_recipe.addAction('Включить')

        mode_menu = self.addMenu('Опции')
        mode_action_group = QActionGroup(self)

        self.__mode_recipe = mode_menu.addAction('Рецепт')
        self.__mode_recipe.setCheckable(True)
        mode_action_group.addAction(self.__mode_recipe)
        self.__mode_recipe.toggled.connect(self.toggle_mode_recipe)

        self.__mode_stat = mode_menu.addAction('Статистика')
        self.__mode_stat.setCheckable(True)
        mode_action_group.addAction(self.__mode_stat)
        self.__mode_stat.toggled.connect(self.toggle_mode_stat)

        help_menu = self.addMenu('Справка')
        self.__about = help_menu.addAction(
            'О программе...')  # public - переменная. Чтобы сделать ее private нужны два подчеркивания вначале: __about
        self.__about_qt = help_menu.addAction('О библиотеке Qt...')
        self.toggle_mode_recipe(False)
        self.toggle_mode_stat(False)

    @pyqtSlot(bool)
    def toggle_mode_recipe(self, enable):
        if not enable:
            self.__recipe_menu_action.setEnabled(False)
            self.__recipe_menu_action.setVisible(False)
            self.__recipe_add.setEnabled(False)
            self.__recipe_edit.setEnabled(False)
            self.__recipe_delete.setEnabled(False)
            self.__recipe_select.setEnabled(False)
        else:
            self.mode_recipe_request.emit()

    @pyqtSlot(bool)
    def toggle_mode_stat(self, enable):
        if not enable:
            self.__stat_menu_action.setEnabled(False)
            self.__stat_menu_action.setVisible(False)
            self.__stat_request.setEnabled(False)
            self.__stat_print.setEnabled(False)
            self.__stat_print_view.setEnabled(False)
            self.__stat_total_action.setEnabled(False)
            self.__stat_total_action.setVisible(False)
            self.__stat_total_run.setEnabled(False)
            self.__stat_recipe_action.setEnabled(False)
            self.__stat_recipe_action.setVisible(False)
            self.__stat_recipe_run.setEnabled(False)
        else:
            self.mode_stat_request.emit()

    @property
    def about(self):
        return self.__about

    @property
    def about_qt(self):
        return self.__about_qt

    def set_mode_recipe(self, widget):
        self.__recipe_add.triggered.connect(widget.add)
        self.__recipe_edit.triggered.connect(widget.update)
        self.__recipe_delete.triggered.connect(widget.delete)
        self.__recipe_select.triggered.connect(widget.select)

        self.__recipe_menu_action.setEnabled(True)
        self.__recipe_menu_action.setVisible(True)
        self.__recipe_add.setEnabled(True)
        self.__recipe_edit.setEnabled(True)
        self.__recipe_delete.setEnabled(True)
        self.__recipe_select.setEnabled(True)

        self.__stat_menu_action.setEnabled(False)
        self.__stat_menu_action.setVisible(False)
        self.__stat_request.setEnabled(False)
        self.__stat_print.setEnabled(False)
        self.__stat_print_view.setEnabled(False)
        self.__stat_total_action.setEnabled(False)
        self.__stat_total_action.setVisible(False)
        self.__stat_total_run.setEnabled(False)
        self.__stat_recipe_action.setEnabled(False)
        self.__stat_recipe_action.setVisible(False)
        self.__stat_recipe_run.setEnabled(False)

    def set_mode_stat(self, widget):
        self.__stat_request.triggered.connect(widget.request)
        self.__stat_print.triggered.connect(widget.handlePrint)
        self.__stat_print_view.triggered.connect(widget.handlePreview)
        self.__stat_total_run.triggered.connect(widget.selectTotalStat)
        self.__stat_recipe_run.triggered.connect(widget.selectStat)

        self.__recipe_menu_action.setEnabled(False)
        self.__recipe_menu_action.setVisible(False)
        self.__recipe_add.setEnabled(False)
        self.__recipe_edit.setEnabled(False)
        self.__recipe_delete.setEnabled(False)
        self.__recipe_select.setEnabled(False)

        self.__stat_menu_action.setEnabled(True)
        self.__stat_menu_action.setVisible(True)
        self.__stat_request.setEnabled(True)
        self.__stat_print.setEnabled(True)
        self.__stat_print_view.setEnabled(True)
        self.__stat_total_action.setEnabled(True)
        self.__stat_total_action.setVisible(True)
        self.__stat_total_run.setEnabled(True)
        self.__stat_recipe_action.setEnabled(True)
        self.__stat_recipe_action.setVisible(True)
        self.__stat_recipe_run.setEnabled(True)