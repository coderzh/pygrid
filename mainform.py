# -*- coding: utf-8 -*-

"""
Module implementing mainWindow.
"""
import os
import sys
import datetime
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# my model
import util
import records
from editdlg import EditDialog
from queryform import QueryWindow
from statform import StatWindow
from Ui_mainform import Ui_mainWindow

class MainWindow(QMainWindow, Ui_mainWindow):
    """
    PyGrid's main window
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)
        
        self.mainSplitter.setStretchFactor(0, 3)
        self.mainSplitter.setStretchFactor(1, 1)
        
        # record model
        colums = [u'日期', u'编号', u'品名', u'类别', u'支出', u'收入', u'余额']
        self.model = records.RecordTableModel(colums)
        self.model.loadRecords(False, records.Record.loadLastRecords, 10)
        self.tableView.setModel(self.model)
        self.tableView.setItemDelegate(records.RecordDelegate(self))
        self.tableView.resizeColumnToContents(0)
        self.tableView.resizeColumnToContents(1)
    
        # category model
        self.categoryModel = records.CategoryModel()
        self.comboBox_Category.setModel(self.categoryModel)
        self.comboBox_SearchCategory.setModel(self.categoryModel)
        self.comboBox_SearchCategory.clearEditText()
        
        self.tableView.addAction(self.action_Edit)
        self.tableView.addAction(self.action_Delete)
        
        # buttonbox
        cancelbutton = self.buttonBox.button(QDialogButtonBox.Cancel)
        cancelbutton.setText(QString(u'重置'))
        cancelbutton.setShortcut(QString(u'Esc'))
        okbutton = self.buttonBox.button(QDialogButtonBox.Ok)
        okbutton.setText(QString(u'插入'))
        okbutton.setShortcut(QString(u'Return'))
        
        self.init_control_data()
    
    def init_control_data(self):
        date_from = records.Setting.GetFirstDate()
        self.dateEdit_Date.setDate(QDate(datetime.date.today()))
        self.dateEdit_From.setDate(QDate(date_from))
        self.dateEdit_To.setDate(QDate(datetime.date.today()))
        self.comboBox_Name.setFocus()
        # update value
        self.update_count_result()
        self.update_doubleSpinBox_Total()
    
    def reset_control_data(self):
        self.comboBox_Name.clearEditText()
        self.doubleSpinBox_InCome.setValue(0.0)
        self.doubleSpinBox_OutCome.setValue(0.0)
        self.comboBox_Name.setFocus()
    
    def update_count_result(self):
        date_from = self.dateEdit_From.date()
        date_to = self.dateEdit_To.date()
        search_name = unicode(self.comboBox_SearchName.currentText().toUtf8(),
                              'utf8',
                              'ignore')
        search_category = unicode(self.comboBox_SearchCategory.currentText().toUtf8(),
                                  'utf8',
                                  'ignore')
        income, outcome, totalleft = records.Record.calculate(date_from,
                                                          date_to,
                                                          search_name,
                                                          search_category)
        self.label_InCome.setText(QString('<font color=darkgreen>%L1</font>').arg(income))
        self.label_OutCome.setText(QString('<font color=red>%L1</font>').arg(outcome))
        self.label_TotalLeft.setText(QString('<font color=blue>%L1</font>').arg(totalleft))
    
    def update_doubleSpinBox_Total(self):
        last_record = self.model.getLastRecord()
        if last_record:
            last_total = last_record.total
        else:
            last_total = 0.0
        income = self.doubleSpinBox_InCome.value()
        outcome = self.doubleSpinBox_OutCome.value()
        self.doubleSpinBox_Total.setValue(last_total + income - outcome)

    def update_settings(self):
        self.categoryModel.updateSettingOfCategorys()
        records.Setting.Update_FirstDate(self.dateEdit_From.date().toPyDate())
    
    @pyqtSignature("")
    def on_action_Query_activated(self):
        """
        Open Query Dialog
        """
        querywindow = QueryWindow(self)
        querywindow.show()
    
    @pyqtSignature("")
    def on_action_Delete_activated(self):
        if QMessageBox.question(self,
            u'提示',
            u'确定要删除所选记录吗？',
            QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            remove_rows = util.getSelectedRows(self.tableView)
            remove_rows.sort()
            remove_rows.reverse()
            for row in remove_rows:
                self.model.removeRows(row)
            
            self.model.save()
            self.update_count_result()
    
    @pyqtSignature("")
    def on_action_Stat_activated(self):
        statwindow = StatWindow(self)
        statwindow.show()
    
    @pyqtSignature("QModelIndex")
    def on_tableView_doubleClicked(self, index):
        record = self.model.getRecord(index)
        editdialog = EditDialog(self, record, self.update_count_result)
        editdialog.show()
        
    @pyqtSignature("")
    def on_action_Edit_activated(self):
        edit_rows = util.getSelectedRows(self.tableView)
        if len(edit_rows) != 1:
            QMessageBox.information(self,
            u'提示',
            u'请仅选择一行进行编辑')
            return
        record = self.model.records[edit_rows[0]]
        editdialog = EditDialog(self, record, self.update_count_result)
        editdialog.show()
    
    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        """
        Add new record
        """
        if self.comboBox_Name.currentText() == '' \
           or self.comboBox_Category.currentText() == '':
            return
        record = records.Record()
        record.name = unicode(self.comboBox_Name.currentText().toUtf8(),'utf8', 'ignore')
        
        record.income = self.doubleSpinBox_InCome.value()
        record.outcome = self.doubleSpinBox_OutCome.value()
        record.category = unicode(self.comboBox_Category.currentText().toUtf8(),
                                  'utf8',
                                  'ignore')
        record.date = self.dateEdit_Date.date().toPyDate()
        
        record.total = self.doubleSpinBox_Total.value()
        
        row = self.model.rowCount()
        self.model.insertRows(row, record)
        self.model.save()
        self.categoryModel.updateCategorys(record.category)
        self.update_count_result()
        self.reset_control_data()

    @pyqtSignature("")
    def on_buttonBox_rejected(self):
        """
        reset
        """
        self.reset_control_data()
        
    @pyqtSignature("double")
    def on_doubleSpinBox_InCome_valueChanged(self, income):
        self.update_doubleSpinBox_Total()
    
    @pyqtSignature("double")
    def on_doubleSpinBox_OutCome_valueChanged(self, outcome):
        self.update_doubleSpinBox_Total()

    @pyqtSignature("QDate")
    def on_dateEdit_From_dateChanged(self, date):
        self.update_count_result()
    
    @pyqtSignature("QDate")
    def on_dateEdit_To_dateChanged(self, date):
        self.update_count_result()
    
    @pyqtSignature("QString")
    def on_comboBox_SearchName_editTextChanged(self, p0):
        self.update_count_result()
    
    @pyqtSignature("QString")
    def on_comboBox_SearchCategory_editTextChanged(self, p0):
        self.update_count_result()

    def closeEvent(self, event):
        self.update_settings()
        #event.accept()
        #event.ignore()
        #QMessageBox.information(self, "abc", "ddd")
        #super(MainWindow, self).close()

if __name__ == "__main__":
    records.initdb()
    app = QApplication(sys.argv)
    mainForm = MainWindow()
    mainForm.show();
    sys.exit(app.exec_())
