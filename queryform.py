# -*- coding: utf-8 -*-

""" Query Dialog """

__author__ = 'CoderZh'

import datetime
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# my model
import util
import records
from editdlg import EditDialog
from Ui_queryform import Ui_MainWindow

class QueryWindow(QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		super(QueryWindow, self).__init__(parent)
		self.setupUi(self)
		self.parent = parent
		colums = [u'日期', u'编号', u'品名', u'类别', u'支出', u'收入']
		self.model = records.RecordTableModel(colums)
		self.tableView.setModel(self.model)
		self.tableView.setItemDelegate(records.RecordDelegate(self))
		
		self.dateEdit_From.setDate(
			QDate(datetime.date.today() - datetime.timedelta(days=30)))
		self.dateEdit_To.setDate(
			QDate(datetime.datetime.now()))
		
		self.categoryModel = self.parent.categoryModel
		self.comboBox_SearchCategory.setModel(self.categoryModel)
		self.comboBox_SearchCategory.clearEditText()
		
		# context menu
		self.tableView.addAction(self.action_Edit)
		self.tableView.addAction(self.action_Delete)
		
		# printer
		self.printer = QPrinter()
		self.printer.setPageSize(QPrinter.Letter)
	
	@pyqtSignature("")
	def on_pushButton_Query_clicked(self):
		date_from = self.dateEdit_From.date()
		date_to = self.dateEdit_To.date()
		search_name = unicode(self.comboBox_SearchName.currentText().toUtf8(),
				      'utf8',
				      'ignore')
		search_category = unicode(self.comboBox_SearchCategory.currentText().toUtf8(),
					  'utf8',
					  'ignore')
		inoutcome = self.comboBox_InOutCome.currentIndex()
		self.model.loadRecords(True,
							   records.Record.getRecords,
							   date_from,
							   date_to,
							   search_name,
							   search_category,
							   inoutcome)
	#@pyqtSignature("QDate")
	#def on_dateEdit_From_dateChanged(self, date):
		#self.update_tableView()
	
	#@pyqtSignature("QDate")
	#def on_dateEdit_To_dateChanged(self, date):
		#self.update_tableView()
	
	#@pyqtSignature("QString")
	#def on_comboBox_SearchName_editTextChanged(self, p0):
		#self.update_tableView()
	
	#@pyqtSignature("QString")
	#def on_comboBox_SearchCategory_editTextChanged(self, p0):
		#self.update_tableView()

	@pyqtSignature("QModelIndex")
	def on_tableView_doubleClicked(self, index):
		record = self.model.getRecord(index)
		editdialog = EditDialog(self, record, self.parent.update_count_result)
		editdialog.show()
		
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
				self.parent.model.loadRecords()
				self.parent.update_count_result()

	@pyqtSignature("")
	def on_action_Edit_activated(self):
		edit_rows = util.getSelectedRows(self.tableView)
		if len(edit_rows) != 1:
			QMessageBox.information(self,
			u'提示',
			u'请仅选择一行进行编辑')
			return
		record = self.model.records[edit_rows[0]]
		editdialog = EditDialog(self,
								record,
								self.parent.update_count_result)
		editdialog.show()
	
	@pyqtSignature("")
	def on_action_Print_activated(self):
		html = self.model.toHtml()
		dialog = QPrintDialog(self.printer, self)
		if dialog.exec_():
			document = QTextDocument()
			document.setHtml(html)
			document.print_(self.printer)
if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	dlg = QueryDialog()
	dlg.show();
	sys.exit(app.exec_())