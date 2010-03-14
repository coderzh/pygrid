# -*- coding: utf-8 -*-

""" Stat Window """

__author__ = 'CoderZh'

import datetime

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import util
import records
from Ui_statform import Ui_MainWindow

class StatWindow(QMainWindow, Ui_MainWindow):
    """
    PyGrid's main window
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        super(StatWindow, self).__init__(parent)
        self.setupUi(self)
	self.parent = parent
        self.dateEdit_From.setDate(QDate(records.Setting.GetFirstDate()))
	self.dateEdit_To.setDate(QDate(datetime.datetime.now()))
        self.categoryModel = self.parent.categoryModel
	self.comboBox_SearchCategory.setModel(self.categoryModel)
	self.comboBox_SearchCategory.clearEditText()
	
	self.printer = QPrinter()
        self.printer.setPageSize(QPrinter.Letter)
	
    @pyqtSignature("")
    def on_pushButton_Stat_clicked(self):
        self.stat_overview()
	self.stat_group_by_name()
	self.stat_group_by_category()
	self.stat_group_by_month()
	self.stat_group_by_year()
    
    @pyqtSignature("")
    def on_action_Print_activated(self):
	html = u''
	date_from = self.dateEdit_From.date().toPyDate().strftime('%Y-%m-%d')
	date_to = self.dateEdit_To.date().toPyDate().strftime('%Y-%m-%d')
	filter_name = unicode(self.comboBox_SearchName.currentText().toUtf8(),
			      'utf8',
			      'ignore')
	filter_category = unicode(self.comboBox_SearchCategory.currentText().toUtf8(),
				  'utf8',
				  'ignore')
	html += u'<h3>从 %s 至 %s 品名:%s 类别:%s</h3>' % (date_from, date_to, filter_name, filter_name)
	for tablewidget in [self.tableWidget_OverView,
			    self.tableWidget_NameGroup,
			    self.tableWidget_CategoryGroup,
			    self.tableWidget_MonthGroup,
			    self.tableWidget_YearGroup]:
	    html += '<p>%s</p>' % util.getHtmlContent(tablewidget)
	dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            document = QTextDocument()
            document.setHtml(html)
            document.print_(self.printer)
    
    def stat(self, tablewidget, stat_func, *args):
	date_from = self.dateEdit_From.date()
	date_to = self.dateEdit_To.date()
	filter_name = unicode(self.comboBox_SearchName.currentText().toUtf8(),
			      'utf8',
			      'ignore')
	filter_category = unicode(self.comboBox_SearchCategory.currentText().toUtf8(),
				  'utf8',
				  'ignore')
	items = stat_func(date_from, date_to, filter_name, filter_category, *args)
	#self.tableWidget_OverView.clear()
	tablewidget.clearContents()
	tablewidget.setSortingEnabled(False)
	tablewidget.setRowCount(len(items))
	for row in range(tablewidget.rowCount()):
	    for col in range(tablewidget.columnCount()):
		item = items[row][col]
		if item is None:
		    item = ''
                if isinstance(item, unicode):
                    pass
                else:
                    item = str(item)
                    
		item = QTableWidgetItem(QString("%1").arg(item))
		tablewidget.setItem(row, col, item)
	tablewidget.setSortingEnabled(True)

    def stat_overview(self):
	self.stat(self.tableWidget_OverView,
		  records.Record.stat_overview)
    def stat_group_by_name(self):
	self.stat(self.tableWidget_NameGroup,
		  records.Record.stat_groupby,
		  'name')
    def stat_group_by_category(self):
	self.stat(self.tableWidget_CategoryGroup,
		  records.Record.stat_groupby,
		  'category')
    def stat_group_by_month(self):
	self.stat(self.tableWidget_MonthGroup,
		  records.Record.stat_groupby,
		  "strftime('%Y-%m', [date])")
    def stat_group_by_year(self):
	self.stat(self.tableWidget_YearGroup,
		  records.Record.stat_groupby,
		  "strftime('%Y', [date])")
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mainForm = StatWindow()
    mainForm.show();
    sys.exit(app.exec_())
    
    
