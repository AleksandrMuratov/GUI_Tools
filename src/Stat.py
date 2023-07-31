from PyQt6.QtWidgets import QTableView, QDialog, QDateTimeEdit, QHeaderView
from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtSql import QSqlQueryModel
from PyQt6.QtCore import pyqtSlot, QSizeF, QMarginsF, Qt
from PyQt6.QtPrintSupport import QPrintDialog, QPrintPreviewDialog, QPrinter
from PyQt6.QtGui import QTextDocument, QTextCursor, QTextTableFormat, QTextCharFormat, QPageLayout, QPageSize

REQUEST = '''
    select
        dt as "Дата и время",
        name_recipe as "Рецепт",
        weight as "Вес замеса",
        fr1 as "Фр 1",
        fr2 as "Фр 2",
        fr3 as "Фр 3",
        fr4 as "Фр 4",
        fr5 as "Фр 5",
        mp as "МП",
        rp as "Пыль",
        bit as "Битум",
        add as "ЦД",
        rfr1 as "Рецепт\nФр 1",
        rfr2 as "Рецепт\nФр 2",
        rfr3 as "Рецепт\nФр 3",
        rfr4 as "Рецепт\nФр 4",
        rfr5 as "Рецепт\nФр 5",
        rmp as "Рецепт\nМП",
        rrp as "Рецепт\nПыль",
        rbit as "Рецепт\nБитум",
        radd as "Рецепт\nЦД"
    from stat
    where dt between to_timestamp('{0}', 'DD-MM-YYYY HH24:MI') and to_timestamp('{1}', 'DD-MM-YYYY HH24:MI')
    union all
    select
        null,
        null,
        sum(weight),
        sum(fr1),
        sum(fr2),
        sum(fr3),
        sum(fr4),
        sum(fr5),
        sum(mp),
        sum(rp),
        sum(bit),
        sum(add),
        sum(rfr1),
        sum(rfr2),
        sum(rfr3),
        sum(rfr4),
        sum(rfr5),
        sum(rmp),
        sum(rrp),
        sum(rbit),
        sum(radd)
    from (
    select
        *
    from stat
    where dt between to_timestamp('{0}', 'DD-MM-YYYY HH24:MI') and to_timestamp('{1}', 'DD-MM-YYYY HH24:MI')) t
    order by "Дата и время";
'''

TOTAL_REQUEST = '''
select
name_recipe as "Рецепт",
sum(weight) as "Отвес",
sum(fr1) as "Фр 1",
sum(fr2) as "Фр 2",
sum(fr3) as "Фр 3",
sum(fr4) as "Фр 4",
sum(fr5) as "Фр 5",
sum(mp) as "МП",
sum(rp) as "Пыль",
sum(bit) as "Битум",
sum(add) as "ЦД"
from (
    select
        *
    from stat
    where dt between to_timestamp('{0}', 'DD-MM-YYYY HH24:MI') and to_timestamp('{1}', 'DD-MM-YYYY HH24:MI')) t
group by "Рецепт"
union all
select
null,
sum(weight),
sum(fr1),
sum(fr2),
sum(fr3),
sum(fr4),
sum(fr5),
sum(mp),
sum(rp),
sum(bit),
sum(add)
from (
    select
        *
    from stat
    where dt between to_timestamp('{0}', 'DD-MM-YYYY HH24:MI') and to_timestamp('{1}', 'DD-MM-YYYY HH24:MI')) t2
'''

class Model(QSqlQueryModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def request(self, date_begin, data_end):
        self.setQuery(REQUEST.format(date_begin, data_end))

    def requestTotal(self, data_begin, data_end):
        self.setQuery(TOTAL_REQUEST.format(data_begin, data_end))

class View(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        model = Model(parent=self)
        self.setModel(model)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setSelectionBehavior(
            self.SelectionBehavior.SelectRows)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.date_begin_ = None
        self.date_end_ = None
        self.__flag_is_total = False

    def request_without_dia(self):
        if self.date_begin_ is None:
            return
        if not self.__flag_is_total:
            self.model().request(self.date_begin_, self.date_end_)
        else:
            self.model().requestTotal(self.date_begin_, self.date_end_)

    @pyqtSlot()
    def selectTotalStat(self):
        self.__flag_is_total = False
        self.request_without_dia()

    @pyqtSlot()
    def selectStat(self):
        self.__flag_is_total = True
        self.request_without_dia()

    @pyqtSlot()
    def request(self):
        dia = Dialog(parent=self)
        if dia.exec():
            self.date_begin_ = dia.date_start
            self.date_end_ = dia.date_finish
            if not self.__flag_is_total:
                self.model().request(dia.date_start, dia.date_finish)
            else:
                self.model().requestTotal(dia.date_start, dia.date_finish)

    @pyqtSlot()
    def handlePrint(self):
        if self.date_begin_ is None:
            return
        dia = QPrintDialog()
        if dia.exec():
            if not self.__flag_is_total:
                self.handlePaintRequest(dia.printer())
            else:
                self.handlePaintRequestTotal(dia.printer())

    @pyqtSlot()
    def handlePreview(self):
        if self.date_begin_ is None:
            return
        dia = QPrintPreviewDialog()
        if not self.__flag_is_total:
            dia.paintRequested.connect(self.handlePaintRequest)
        else:
            dia.paintRequested.connect(self.handlePaintRequestTotal)
        dia.exec()

    def handlePaintRequestTotal(self, printer):
        document = QTextDocument()
        rct = printer.pageRect(QPrinter.Unit.Millimeter)
        page_layout = QPageLayout(QPageSize(QSizeF(rct.width(), rct.height()), QPageSize.Unit.Millimeter),
                                  QPageLayout.Orientation.Landscape, QMarginsF(0, 0, 0, 0), QPageLayout.Unit.Millimeter)
        printer.setPageLayout(page_layout)
        cursor = QTextCursor(document)
        cursor.insertHtml('<h2 align="center" style="color: black;" >Статистика по рецептам за период<br></h2>')
        cursor.insertHtml(
            '<h2 align="center" style="color: black;" >c {0} по {1}<br></h2>'.format(self.date_begin_, self.date_end_))
        model = self.model()
        fmt_table = QTextTableFormat()
        fmt_table.clearColumnWidthConstraints()
        fmt_table.setCellPadding(5)
        fmt_table.setCellSpacing(0)
        fmt_table.setHeaderRowCount(1)
        fmt_table.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        fmt_text = QTextCharFormat()
        fmt_text.setFontPointSize(12)
        table = cursor.insertTable(
            model.rowCount() + 1, model.columnCount(), fmt_table)
        cursor.insertText('Рецепт')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Отвес')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Фр 1')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Фр 2')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Фр 3')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Фр 4')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Фр 5')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('МП')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Пыль')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Битум')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('ЦД')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        for row in range(table.rows() - 1):
            for column in range(table.columns()):
                if column == 0 and row == table.rows() - 2:
                    cursor.insertText('Суммарно', fmt_text)
                elif column == 0:
                    cursor.insertText(model.data(model.index(row, column)), fmt_text)
                else:
                    cursor.insertText(f'{model.data(model.index(row, column)):.1f}', fmt_text)
                cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        document.print(printer)


    def handlePaintRequest(self, printer):
        document = QTextDocument()
        rct = printer.pageRect(QPrinter.Unit.Millimeter)
        page_layout = QPageLayout(QPageSize(QSizeF(rct.width(), rct.height()), QPageSize.Unit.Millimeter),
                                  QPageLayout.Orientation.Landscape, QMarginsF(0, 0, 0, 0), QPageLayout.Unit.Millimeter)
        printer.setPageLayout(page_layout)
        cursor = QTextCursor(document)
        cursor.insertHtml('<h2 align="center" style="color: black;" >Статистика за период<br></h2>')
        cursor.insertHtml(
            '<h2 align="center" style="color: black;" >c {0} по {1}<br></h2>'.format(self.date_begin_, self.date_end_))
        model = self.model()
        fmt_table = QTextTableFormat()
        fmt_table.clearColumnWidthConstraints()
        fmt_table.setCellPadding(2)
        fmt_table.setCellSpacing(0)
        fmt_table.setHeaderRowCount(1)
        fmt_text = QTextCharFormat()
        fmt_text.setFontPointSize(7)
        table = cursor.insertTable(
            model.rowCount() + 1, model.columnCount(), fmt_table)
        cursor.insertText('Дата и время')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Рецепт')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Вес замеса')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Фр 1')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Фр 2')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Фр 3')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Фр 4')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Фр 5')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('МП')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Пыль')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Битум')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('ЦД')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Рецепт\nФр 1')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Рецепт\nФр 2')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Рецепт\nФр 3')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Рецепт\nФр 4')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Рецепт\nФр 5')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Рецепт\nМП')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Рецепт\nПыль')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Рецепт\nБитум')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        cursor.insertText('Рецепт\nЦД')
        cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        for row in range(table.rows() - 1):
            for column in range(table.columns()):
                if column == 0 and row != table.rows() - 2:
                    cursor.insertText(model.data(model.index(row, column)).toString('dd-MM-yyyy hh:mm'), fmt_text)
                elif column == 0 and row == table.rows() - 2:
                    cursor.insertText('Суммарно', fmt_text)
                elif column == 1:
                    cursor.insertText(model.data(model.index(row, column)), fmt_text)
                else:
                    cursor.insertText(f'{model.data(model.index(row, column)):.1f}', fmt_text)
                cursor.movePosition(QTextCursor.MoveOperation.NextCell)
        document.print(printer)

class Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        date_start = QLabel('Начальная дата', parent=self)
        self.__date_start = QDateTimeEdit(parent=self)

        date_finish = QLabel('Конечная дата', parent=self)
        self.__date_finish = QDateTimeEdit(parent=self)

        ok_btn = QPushButton('OK', parent=self)
        cancel_btn = QPushButton('Отмена', parent=self)

        lay = QVBoxLayout(self)
        lay.addWidget(date_start)
        lay.addWidget(self.__date_start)
        lay.addWidget(date_finish)
        lay.addWidget(self.__date_finish)
        lay2 = QHBoxLayout()
        lay2.addWidget(ok_btn)
        lay2.addWidget(cancel_btn)
        lay.addLayout(lay2)

        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.finish)

    @pyqtSlot()
    def finish(self):
        if self.date_start is None or self.date_finish is None:
            return
        self.accept()

    @property
    def date_start(self):
        result = str(self.__date_start.dateTime().toString('dd-MM-yyyy hh:mm'))
        if result == '':
            return None
        else:
            return result

    @property
    def date_finish(self):
        result = str(self.__date_finish.dateTime().toString('dd-MM-yyyy hh:mm'))
        if result == '':
            return None
        else:
            return result
