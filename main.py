
# checks to see if the 'PyQT5' module is installed
try: 
    from PyQt5.QtWidgets import QWidget, QApplication, QTableWidgetItem, QMessageBox
    from PyQt5.QtSql import QSqlQuery, QSqlDatabase
    from PyQt5.QtCore import QDate
    from PyQt5 import uic
except ModuleNotFoundError: # if it's not then it will automatically be installed
    print("PyQT5 module is not installed")
    import subprocess
    required_packages = ['PyQT5']
    for package in required_packages:
        subprocess.call(['pip', 'install', package])

import sys
from PyQt5.QtWidgets import QWidget, QApplication, QTableWidgetItem, QMessageBox
from PyQt5.QtSql import QSqlQuery, QSqlDatabase
from PyQt5.QtCore import QDate
from PyQt5 import uic


# automatically create a new database
database = QSqlDatabase.addDatabase("QSQLITE")
database.setDatabaseName("expenses.db")
if not database.open():
    QMessageBox.critical(None, "Error","Could not open your database")
    sys.exit(1)

query = QSqlQuery()
query.exec_("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                category TEXT,
                amount INTEGER,
                description TEXT
            )
            """)

class UI(QWidget):  
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self) #load the UI file

        #define our widgets
        self.add_button.clicked.connect(self.add_expense)
        self.update_button.clicked.connect(self.update_expense)
        self.delete_button.clicked.connect(self.delete_expense)
        self.delete_all_button.clicked.connect(self.delete_all)
    
        self.load_table()

    def load_table(self):
        self.date_box.setDate(QDate.currentDate())
        self.table.setRowCount(0)

        query = QSqlQuery("SELECT * FROM expenses")
        row = 0
        while query.next(): # while loop to query all the rows in the database
            expense_id = query.value(0)
            date = query.value(1)
            category = query.value(2)
            amount = query.value(3)
            description = query.value(4)

            # and add them to the table
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(expense_id)))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(category))
            self.table.setItem(row, 3, QTableWidgetItem(str(amount)))
            self.table.setItem(row, 4, QTableWidgetItem(description))

            row += 1

    def add_expense(self):
        date = self.date_box.date().toString("MM-dd-yyyy")
        category = self.dropdown.currentText()
        amount = self.amount.text() # value taken from the QLineEdit which is text
        description = self.description.text() # value taken from the QLineEdit which is text

        query = QSqlQuery()
        query.prepare("""
                    INSERT INTO expenses (date, category, amount, description)
                    VALUES(?, ?, ?, ?)
                    """)
        query.addBindValue(date)
        query.addBindValue(category)
        query.addBindValue(amount)
        query.addBindValue(description)
        query.exec_()

        # clear these fields for the next query
        self.date_box.setDate(QDate.currentDate())
        self.dropdown.setCurrentIndex(0)
        self.amount.clear()
        self.description.clear()

        self.load_table() # this will load the database back into the table with the updated information

    def delete_expense(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "no expense chosen", "please choose an expense to delete")
            return

        expense_id = int(self.table.item(selected_row, 0).text())

        confirm = QMessageBox.question(self, "Are you sure?", "Delete Expense?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        query = QSqlQuery()
        query.prepare("DELETE FROM expenses WHERE id = ?")
        query.addBindValue(expense_id)

        query.exec_()

        self.load_table()

    def update_expense(self):
        date = self.date_box.date().toString("MM-dd-yyyy")
        category = self.dropdown.currentText()
        amount = self.amount.text() # value taken from the QLineEdit which is text
        description = self.description.text() # value taken from the QLineEdit which is text

        selected_row = self.table.currentRow()
 
        if selected_row == -1:
            QMessageBox.warning(self, "no expense chosen", "please choose an expense to update")
            return
        
        expense_id = int(self.table.item(selected_row, 0).text())
        date = self.table.item(selected_row, 1).text()
        category = self.table.item(selected_row, 2).text()
        amount = self.table.item(selected_row, 3).text()
        description = self.table.item(selected_row, 4).text()

        confirm = QMessageBox.question(self, "Are you sure?", "Update Expense?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        query = QSqlQuery()
        
        query.prepare("""
                      UPDATE expenses SET date = ?, category = ?, amount = ?, description = ? WHERE id = ?
                      """)
        
        query.addBindValue(date)
        query.addBindValue(category)
        query.addBindValue(amount)
        query.addBindValue(description)
        query.addBindValue(expense_id)

        query.exec_()

        self.load_table()

    def delete_all(self):
        confirm = QMessageBox.question(self, "Are you sure?", "Are you sure you want to delete?", QMessageBox.Yes | QMessageBox.No)
        match confirm:
            case QMessageBox.No:
                return
            case QMessageBox.Yes:
                confirm2  = QMessageBox.question(self, "Are you sure?", "Dude, are you like really sure you want to delete?", QMessageBox.Yes | QMessageBox.No)
                match confirm2:
                    case QMessageBox.No:
                        return

        query = QSqlQuery()
        query.prepare("DELETE FROM expenses")

        query.exec_()

        self.load_table()

# Show/Run app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = UI()
    UIWindow.show()
    app.exec_()