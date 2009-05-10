# -*- coding: utf-8 -*-

from Ui_editdlg import Ui_Dialog
from PyQt4.QtGui import *
from PyQt4.QtCore import *
class EditDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None, record=None, *after_calls):
        super(EditDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.record = record
        self.after_calls = after_calls
        self.comboBox_Category.setModel(parent.categoryModel)
        if self.record:
            self.setWindowTitle(QString(u'编辑 - 编号:%1').arg(self.record.id))

        # buttonbox
        cancelbutton = self.buttonBox.button(QDialogButtonBox.Cancel)
        cancelbutton.setText(QString(u'取消'))
        okbutton = self.buttonBox.button(QDialogButtonBox.Ok)
        okbutton.setText(QString(u'插入'))
        okbutton.setShortcut(QString(u'Return'))

        self.fill_data()
        
        self.comboBox_Name.setFocus()
        
    
    def fill_data(self):
        '''
        fill the edits with record
        '''
        self.comboBox_Name.setEditText(QString(u'%1').arg(self.record.name))
        self.doubleSpinBox_OutCome.setValue(self.record.outcome)
        self.doubleSpinBox_InCome.setValue(self.record.income)
        self.doubleSpinBox_Total.setValue(self.record.total)
        self.comboBox_Category.setEditText(QString(u'%1').arg(self.record.category))
        self.dateEdit_Date.setDate(QDate(self.record.date))
    
    def accept(self):
        '''
        modify the record and close this dialog
        '''
        self.record.name = unicode(self.comboBox_Name.currentText().toUtf8(),
                                   'utf8',
                                   'ignore')
        self.record.outcome = self.doubleSpinBox_OutCome.value()
        self.record.income = self.doubleSpinBox_InCome.value()
        self.record.total = self.doubleSpinBox_Total.value()
        self.record.category = unicode(self.comboBox_Category.currentText().toUtf8(),
                                       'utf8',
                                       'ignore')
        self.record.date = self.dateEdit_Date.date().toPyDate()
        self.parent.model.save()
        self.parent.categoryModel.updateCategorys(self.record.category)
        for after_call in self.after_calls:
            after_call()
        self.close()

    def update_doubleSpinBox_Total(self):
        income = self.doubleSpinBox_InCome.value()
        outcome = self.doubleSpinBox_OutCome.value()
        if not hasattr(self, 'totalbase'):
            self.totalbase = self.record.total + self.record.outcome - self.record.income
        self.doubleSpinBox_Total.setValue(self.totalbase + income - outcome)
    
    @pyqtSignature("double")
    def on_doubleSpinBox_OutCome_valueChanged(self, outcome):
        self.update_doubleSpinBox_Total()
    
    @pyqtSignature("double")
    def on_doubleSpinBox_InCome_valueChanged(self, income):
        self.update_doubleSpinBox_Total()
        
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dlg = EditDialog()
    dlg.show();
    sys.exit(app.exec_())