from PyQt6.QtWidgets import QTableView, QMessageBox, QDialog, QHeaderView
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtSql import QSqlQueryModel
from PyQt6.QtCore import pyqtSlot
import psycopg
import settings as st

INSERT = '''
    insert into recipes(name, fr1, fr2, fr3, fr4, fr5, mp, rp, bit, add)
        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
'''

SELECT_ONE = '''
    select name, fr1, fr2, fr3, fr4, fr5, mp, rp, bit, add
        from recipes
        where id = %s;
'''

UPDATE_RECIPE = '''
    update recipes set
        name = %s,
        fr1 = %s,
        fr2 = %s,
        fr3 = %s,
        fr4 = %s,
        fr5 = %s,
        mp = %s,
        rp = %s,
        bit = %s,
        add = %s
    where id = %s;
'''

UPDATE_CURRENT = '''
    with temp as (select * from current_recipe)
    update current_recipe set
        id = %s,
        name = %s,
        fr1 = %s,
        fr2 = %s,
        fr3 = %s,
        fr4 = %s,
        fr5 = %s,
        mp = %s,
        rp = %s,
        bit = %s,
        add = %s
    where id in (select id from temp);
'''

DELETE = '''
    delete from recipes where id = %s;
'''


class Model(QSqlQueryModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.obnovit()

    def obnovit(self):
        sql = '''
        select
        id,
        name as Рецепт,
        fr1 as "Фр.1",
        fr2 as "Фр.2",
        fr3 as "Фр.3",
        fr4 as "Фр.4",
        fr5 as "Фр.5",
        mp as "Минеральный\nпорошок",
        rp as Пыль,
        bit as Битум,
        add as "Целлюлозная\nдобавка"
        from current_recipe
        union all
        select
        id,
        name as Рецепт,
        fr1 as "Фр.1",
        fr2 as "Фр.2",
        fr3 as "Фр.3",
        fr4 as "Фр.4",
        fr5 as "Фр.5",
        mp as "Минеральный\nпорошок",
        rp as Пыль,
        bit as Битум,
        add as "Целлюлозная\nдобавка"
        from recipes;
        '''
        self.setQuery(sql)

    def add(self, name, fr1, fr2, fr3, fr4, fr5, mp, rp, bit, additive):
        conn = psycopg.connect(**st.db_params)
        cursor = conn.cursor()
        data = (name, fr1, fr2, fr3, fr4, fr5, mp, rp, bit, additive)
        cursor.execute(INSERT, data)  # отправить данные
        conn.commit()  # завершить транзакцию
        conn.close()
        self.obnovit()

    def update(self, id_recipe, name, fr1, fr2, fr3, fr4, fr5, mp, rp, bit, additive):
        conn = psycopg.connect(**st.db_params)
        cursor = conn.cursor()
        data = (name, fr1, fr2, fr3, fr4, fr5, mp, rp, bit, additive, id_recipe)
        cursor.execute(UPDATE_RECIPE, data)  # отправить данные
        conn.commit()  # завершить транзакцию
        conn.close()
        self.obnovit()

    def delete(self, id_recipe):
        conn = psycopg.connect(**st.db_params)
        cursor = conn.cursor()
        data = (id_recipe,)
        cursor.execute(DELETE, data)  # отправить данные
        conn.commit()  # завершить транзакцию
        conn.close()
        self.obnovit()

    def select(self, id_recipe, name, fr1, fr2, fr3, fr4, fr5, mp, rp, bit, additive):
        conn = psycopg.connect(**st.db_params)
        cursor = conn.cursor()
        data = (id_recipe, name, fr1, fr2, fr3, fr4, fr5, mp, rp, bit, additive)
        cursor.execute(UPDATE_CURRENT, data)
        conn.commit()  # завершить транзакцию
        conn.close()
        self.obnovit()

class View(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        model = Model(parent=self)
        self.setModel(model)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows) #выделение всей строки при выборе, а не только одной ячейки
        self.setSelectionMode(self.SelectionMode.SingleSelection)#запрет выбора нескольких строк
        self.hideColumn(0)#скрыть столбец 0
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

    @pyqtSlot()
    def add(self):
        dia = Dialog(parent=self)
        if dia.exec():
            self.model().add(dia.name, dia.fr1, dia.fr2, dia.fr3,
                             dia.fr4, dia.fr5, dia.mp, dia.rp, dia.bit, dia.additive)

    @pyqtSlot()
    def update(self):
        row = self.currentIndex().row()  # выбор выделенной строки
        if row == 0:
            return
        id_recipe = self.model().record(row).value(0)  # выбор ячейки 0
        dia = Dialog(parent=self)
        conn = psycopg.connect(**st.db_params)
        cursor = conn.cursor()
        data = (id_recipe,)
        cursor.execute(SELECT_ONE, data)
        dia.name, dia.fr1, dia.fr2, dia.fr3, dia.fr4, dia.fr5, dia.mp, dia.rp, dia.bit, dia.additive = cursor.fetchone()  # считать одну строчку из таблицы
        conn.close()
        if dia.exec():
            self.model().update(id_recipe, dia.name, dia.fr1, dia.fr2, dia.fr3,
                                dia.fr4, dia.fr5, dia.mp, dia.rp, dia.bit, dia.additive)

    @pyqtSlot()
    def delete(self):
        row = self.currentIndex().row()  # выбор выделенной строки
        if row == 0:
            return
        id_recipe = self.model().record(row).value(0)  # выбор ячейки 0
        ans = QMessageBox.question(self, 'Рецепт', 'Вы уверены?')
        if ans == QMessageBox.StandardButton.Yes:
            self.model().delete(id_recipe)

    @pyqtSlot()
    def select(self):
        row = self.currentIndex().row()  # выбор выделенной строки
        if row == 0:
            return
        id_recipe = self.model().record(row).value(0)  # выбор ячейки 0
        conn = psycopg.connect(**st.db_params)
        cursor = conn.cursor()
        data = (id_recipe,)
        cursor.execute(SELECT_ONE, data)
        name, fr1, fr2, fr3, fr4, fr5, mp, rp, bit, additive = cursor.fetchone()  # считать одну строчку из таблицы
        conn.close()
        self.model().select(id_recipe, name, fr1, fr2, fr3, fr4, fr5, mp, rp, bit, additive)


class Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        name = QLabel('Имя рецепта', parent=self)
        self.__name = QLineEdit(parent=self)

        fr1 = QLabel('Фракция 1', parent=self)
        self.__fr1 = QLineEdit(parent=self)

        fr2 = QLabel('Фракция 2', parent=self)
        self.__fr2 = QLineEdit(parent=self)

        fr3 = QLabel('Фракция 3', parent=self)
        self.__fr3 = QLineEdit(parent=self)

        fr4 = QLabel('Фракция 4', parent=self)
        self.__fr4 = QLineEdit(parent=self)

        fr5 = QLabel('Фракция 5', parent=self)
        self.__fr5 = QLineEdit(parent=self)

        mp = QLabel('Минеральный порошок', parent=self)
        self.__mp = QLineEdit(parent=self)

        rp = QLabel('Пыль', parent=self)
        self.__rp = QLineEdit(parent=self)

        bit = QLabel('Битум', parent=self)
        self.__bit = QLineEdit(parent=self)

        additive = QLabel('Целлюлозная добавка', parent=self)
        self.__additive = QLineEdit(parent=self)

        ok_btn = QPushButton('OK', parent=self)
        cancel_btn = QPushButton('Отмена', parent=self)

        lay = QVBoxLayout(self)
        lay.addWidget(name)
        lay.addWidget(self.__name)
        lay.addWidget(fr1)
        lay.addWidget(self.__fr1)
        lay.addWidget(fr2)
        lay.addWidget(self.__fr2)
        lay.addWidget(fr3)
        lay.addWidget(self.__fr3)
        lay.addWidget(fr4)
        lay.addWidget(self.__fr4)
        lay.addWidget(fr5)
        lay.addWidget(self.__fr5)
        lay.addWidget(mp)
        lay.addWidget(self.__mp)
        lay.addWidget(rp)
        lay.addWidget(self.__rp)
        lay.addWidget(bit)
        lay.addWidget(self.__bit)
        lay.addWidget(additive)
        lay.addWidget(self.__additive)
        lay2 = QHBoxLayout()
        lay2.addWidget(ok_btn)
        lay2.addWidget(cancel_btn)
        lay.addLayout(lay2)

        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.finish)

    @pyqtSlot()
    def finish(self):
        if self.name is None:
            return
        self.accept()

    @property
    def name(self):
        result = self.__name.text().strip()
        if result == '':
            return None
        else:
            return result

    @name.setter
    def name(self, value):
        self.__name.setText(value)

    @property
    def fr1(self):
        result = self.__fr1.text().strip()
        if result == '':
            return None
        else:
            return result

    @fr1.setter
    def fr1(self, value):
        self.__fr1.setText(str(value))

    @property
    def fr2(self):
        result = self.__fr2.text().strip()
        if result == '':
            return None
        else:
            return result

    @fr2.setter
    def fr2(self, value):
        self.__fr2.setText(str(value))

    @property
    def fr3(self):
        result = self.__fr3.text().strip()
        if result == '':
            return None
        else:
            return result

    @fr3.setter
    def fr3(self, value):
        self.__fr3.setText(str(value))

    @property
    def fr4(self):
        result = self.__fr4.text().strip()
        if result == '':
            return None
        else:
            return result

    @fr4.setter
    def fr4(self, value):
        self.__fr4.setText(str(value))

    @property
    def fr5(self):
        result = self.__fr5.text().strip()
        if result == '':
            return None
        else:
            return result

    @fr5.setter
    def fr5(self, value):
        self.__fr5.setText(str(value))

    @property
    def mp(self):
        result = self.__mp.text().strip()
        if result == '':
            return None
        else:
            return result

    @mp.setter
    def mp(self, value):
        self.__mp.setText(str(value))

    @property
    def rp(self):
        result = self.__rp.text().strip()
        if result == '':
            return None
        else:
            return result

    @rp.setter
    def rp(self, value):
        self.__rp.setText(str(value))

    @property
    def bit(self):
        result = self.__bit.text().strip()
        if result == '':
            return None
        else:
            return result

    @bit.setter
    def bit(self, value):
        self.__bit.setText(str(value))

    @property
    def additive(self):
        result = self.__additive.text().strip()
        if result == '':
            return None
        else:
            return result

    @additive.setter
    def additive(self, value):
        self.__additive.setText(str(value))
