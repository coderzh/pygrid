# -*- coding: utf-8 -*-
#from PyQt4.QtGui import *
#from PyQt4.QtCore import *
import sys,os

def getSelectedRows(tableView):
    rows = []
    for index in tableView.selectedIndexes():
        if index.column() == 0:
            rows.append(index.row())
    return rows

def getHtmlContent(tableWidget):
    #tableWidget = QTableWidget()
    rows = tableWidget.rowCount()
    cols = tableWidget.columnCount()
    
    html = u'<table border=1 cellpadding=3 cellspacing=0><tr bgcolor="#808080">'
    
    # add header
    for c in range(cols):
        header = tableWidget.horizontalHeaderItem(c).text()
        html += '<th><font color="#FFFFFF">%s</font></th>' % header
        
    # add items
    for r in range(rows):
        html += '<tr>'
        for c in range(cols):
            text = tableWidget.item(r, c).text()
            html += '<td>%s</td>' % text
        html += '</tr>'
    
    # end table
    html += '</table>'
    return html

def initlog():
    import logging
    logger = logging.getLogger()
    logfile = 'test.log'
    hdlr = logging.FileHandler('sendlog.txt')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger