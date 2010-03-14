#coding=utf-8

import os
import datetime

from elixir import *
# from sqlalchemy.orm import sessionmaker
#from sqlalchemy import desc

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import util

R_DATE, R_ID, R_NAME, R_CATEGORY, R_OUTCOME, R_INCOME, R_TOTAL = range(7)

class Record(Entity):
    number = Field(Integer, default=1)
    name = Field(Unicode(60), required=True)
    category = Field(Unicode(60), required=True)
    income = Field(Float, default=0.0)
    outcome = Field(Float, default=0.0)
    #total = Field(Float, required=True)
    date = Field(Date, default=datetime.date.today(), required=True)
    #order = Field(Integer, default=0)
    using_options(tablename='records')
    
    total = 0.0
    
    def __cmp__(self, other):
        return QString.localeAwareCompare(self.name.toLower(), other.name.toLower())

    def __repr__(self):
        return self.name
    
    @staticmethod
    def get_sql_filter_condition(date_from, date_to, filter_name, filter_category):
        params = {}
        condition = 'where [date] >= date(:date_from) and [date] <= date(:date_to)'
            
        params['date_from'] = unicode(date_from.toString('yyyy-MM-dd').toUtf8(),
                                      'utf8',
                                      'ignore')
        params['date_to'] = unicode(date_to.toString('yyyy-MM-dd').toUtf8(),
                                    'utf8',
                                    'ignore')
        if filter_name != '':
            condition += ' and [name] = :filter_name'
            params['filter_name'] = filter_name
        if filter_category != '':
            condition += ' and [category] = :filter_category'
            params['filter_category'] = filter_category
            
        return condition, params
    
    @staticmethod
    def calculate(date_from, date_to, filter_name, filter_category):
        result = Record.stat_overview(date_from, 
                             date_to, 
                             filter_name, 
                             filter_category)[0]
        income = result[0]
        outcome = result[1]
        total = result[2]
        if not income:
            income = 0.0
        if not outcome:
            outcome = 0.0
        if not total:
            total = 0.0
        return income, outcome, total
    
    @staticmethod
    def stat_overview(date_from, date_to, filter_name, filter_category):
        sql = 'select sum([outcome]) as outcome,'\
            'sum([income]) as income '\
            'from [records]'
        condition, params = Record.get_sql_filter_condition(date_from, 
                                            date_to, 
                                            filter_name, 
                                            filter_category)
        sql = 'select outcome,'\
            'income,'\
            '(income-outcome) as total '\
            'from (%s %s)' % (sql, condition)
        return session.execute(sql, params).fetchall()
    
    @staticmethod
    def stat_groupby(date_from, date_to, filter_name, filter_category, group_name):
        sql = 'select %s as name,'\
            'sum([outcome]) as outcome,'\
            'sum([income]) as income '\
            'from [records]' % group_name
        condition, params = Record.get_sql_filter_condition(date_from, 
                                            date_to, 
                                            filter_name, 
                                            filter_category)
        sql = 'select name,'\
            'outcome,'\
            'income,'\
            '(income-outcome) as total '\
            'from (%s %s group by %s)' % (sql, condition, group_name)
        return session.execute(sql, params).fetchall()
    
    
    @staticmethod
    def loadLastRecords(recordCount):
        recordcount = Record.query.count()
        if recordcount == 0:
            return []
        previous_total = 0.0
        if recordcount > recordCount:
            count = recordcount - recordCount
            result = session.execute('select sum(income)-sum(outcome) as totalleft from (select * from records order by [number] limit :count)',
                                     {'count' : count}).fetchone()
            previous_total = result['totalleft']
        
        records = Record.query.order_by(Record.number)[-recordCount:]
        first_record = records[0]
        first_record.total = previous_total + first_record.income - first_record.outcome
        return records

    @staticmethod
    def getRecords(date_from, date_to, search_name, search_category, inoutcome=0):
        query = Record.query.filter(Record.date >= date_from.toPyDate())
        query = query.filter(Record.date <= date_to.toPyDate())
        if search_name != '':
            query = query.filter(Record.name == search_name)
        if search_category != '':
            query = query.filter(Record.category == search_category)
        if inoutcome == 1:
            query = query.filter(Record.outcome > 0)
        elif inoutcome == 2:
            query = query.filter(Record.income > 0)
        return query.order_by(Record.number).all()

S_TITLE, S_CATEGORYS, S_FIRSTDATE = u'Title', u'Categorys', u'FirstDate'

class Setting(Entity):
    name = Field(Unicode(60), primary_key=True)
    value = Field(UnicodeText(1024))
    using_options(tablename='settings')
    def __cmp__(self, other):
        return QString.localeAwareCompare(self.name.toLower(), other.name.toLower())
    def __repr__(self):
        return self.name
    
    @staticmethod
    def GetTitle():
        s = Setting.query.filter_by(name=S_TITLE).first()
        if s:
            return s.value
        s = Setting(name=S_TITLE, value=u'PyGrid')
        session.commit()
        return s.value
    @staticmethod
    def GetCategorys():
        s = Setting.query.filter_by(name=S_CATEGORYS).first()
        if s:
            return s.value
        s = Setting(name=S_CATEGORYS, value=u'')
        session.commit()
        return s.value
    @staticmethod
    def GetFirstDate():
        s = Setting.query.filter_by(name=S_FIRSTDATE).first()
        if s:
            return datetime.datetime.strptime(s.value, '%Y-%m-%d')
        s = Setting(name=S_FIRSTDATE,
                    value=unicode(datetime.date.today().strftime('%Y-%m-%d')))
        session.commit()
        return datetime.date.today()
    
    @staticmethod
    def Update_Categorys():
        categorys = ','.join([item['category'] for item in \
                         session.execute('select distinct category from records')])
        item = Setting.query.filter_by(name=S_CATEGORYS).first()
        if not item:
            item = Setting(name=S_CATEGORYS, value=categorys)
        else:
            item.value = categorys
        session.commit()
        
    @staticmethod
    def Update_FirstDate(firstdate):
        item = Setting.query.filter_by(name=S_FIRSTDATE).first()
        if not item:
            item = Setting(name=S_FIRSTDATE, value=firstdate.strftime('%Y-%m-%d'))
        else:
            item.value = firstdate.strftime('%Y-%m-%d')
        session.commit()
        
'''
Custom Table Models
'''
class RecordTableModel(QAbstractTableModel):
    def __init__(self, columns):
        super(RecordTableModel, self).__init__()
        self.columns = columns
        self.loader = None
        self.args = ()
        self.loadRecords()
    
    def loadRecords(self, reset=True, recordloader=None, *loaderArgs):
        self.records = []
        if recordloader:
            self.loader = recordloader
            self.args = loaderArgs
        if self.loader:
            self.records = self.loader(*self.args)
        if reset:
            self.reset()
    
    def setRecordsLoader(self, loader):
        self.loader = loader
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.records)

    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        record = self.getRecord(index)
        if not record:
            return QVariant()
        column = index.column()
        if role == Qt.DisplayRole:
            if column == R_NAME:
                return QVariant(QString(record.name))
            elif column ==R_ID:
                return QVariant(QString(u'%1').arg(record.number))
            elif column == R_INCOME and record.income > 0:
                return QVariant(QString(u'%L1').arg(record.income))
            elif column == R_OUTCOME and record.outcome > 0:
                return QVariant(QString(u'%L1').arg(record.outcome))
            elif column == R_TOTAL:
                income = 0.0
                outcome = 0.0
                if index.row() > 0:
                    record.total = self.records[index.row()-1].total \
                          + record.income \
                          - record.outcome
                
                return QVariant(QString(str(record.total)))
            elif column == R_CATEGORY:
                return QVariant(QString(record.category))
            elif column == R_DATE:
                return QVariant(QDate(record.date).toString(u'yyyy-MM-dd'))
        elif role == Qt.TextColorRole:
            if column == R_INCOME:
                return QVariant(QColor(Qt.darkGreen))
            elif column == R_OUTCOME:
                return QVariant(QColor(Qt.red))
            elif column == R_TOTAL:
                return QVariant(QColor(Qt.blue))
        return QVariant()
        
    def headerData(self, col, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.columns[col])
        return QVariant()
        
    def getRecord(self, index):
        if not index.isValid() or not (0 <= index.row() < len(self.records)):
            return None
        return self.records[index.row()]
    
    def insertRows(self, position, new_record, rows=1, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for row in range(rows):
            self.records.insert(position + row, new_record)
        self.endInsertRows()
        # self.dirty = True
        return True
        
    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(index, position,
                             position + rows - 1)
        self.records[position].delete()
        self.records = self.records[:position] + \
                     self.records[position + rows:]
        self.endRemoveRows()
        # self.dirty = True
        return True
    
    def save(self):
        # if self.dirty:
        session.commit()
            # self.dirty = False
    
    def getLastRecord(self):
        if len(self.records) > 0:
            return self.records[-1]
        return None
    
    def toHtml(self):
        html = u'<table border=1 cellpadding=3 cellspacing=0><tr bgcolor="#808080">'
        # header
        for col in self.columns:
            html += '<th><font color="#FFFFFF">%s</font></th>' % col
        # content
        for record in self.records:
            html += '<tr>'
            html += '<td>%s</td>' % record.date.strftime('%Y-%m-%d')
            html += '<td>%d</td>' % record.number
            html += '<td>%s</td>' % record.name
            html += '<td>%s</td>' % record.category
            html += '<td>%d</td>' % record.income
            html += '<td>%d</td>' % record.outcome
            html += '</tr>'
        html += '</table>'
        return html
            

class CategoryModel(QAbstractListModel):
    def __init__(self):
        super(CategoryModel, self).__init__()
        self.categorys = []
        s_categorys = Setting.GetCategorys()
        self.categorys = s_categorys.split(',')
        self.dirty = False
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.categorys)

    def data(self, index, role=Qt.DisplayRole):
        category = self.getCurrentCategory(index)
        if not category:
            return QVariant()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            '''
            Important, add (role == Qt.EditRole)
            '''
            return QVariant(category)
        return QVariant()
    
    def getCurrentCategory(self, index):
        if not index.isValid() or not (0 <= index.row() < len(self.categorys)):
            return None
        return self.categorys[index.row()]
    
    def updateCategorys(self, name):
        for category in self.categorys:
            if category == name:
                return
        self.insertRows(self.rowCount(), name)

    def updateSettingOfCategorys(self):
        if self.dirty:
            Setting.Update_Categorys()
    
    def insertRows(self, position, new_category, rows=1, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for row in range(rows):
            self.categorys.insert(position + row, new_category)
        self.endInsertRows()
        self.dirty = True
        return True
'''
Custom Delegate
'''
class RecordDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(RecordDelegate, self).__init__(parent)
    
    #def createEditor(self, parent, option, index):
        #return QItemDelegate.createEditor(self, parent, option, index)
    #def sizeHint(self, option, index):
        #fm = option.fontMetrics
        #if index.column() == R_ID:
            #return QSize(fm.width('9,999,999'), fm.height())

dbdir = os.path.join(os.getcwd(), "db")
    
def initdb():
    if not os.path.isdir(dbdir):
        os.mkdir(dbdir)

    dbfile = os.path.join(dbdir, "data.sqlite")
        
    metadata.bind = "sqlite:///%s" % dbfile
    session.bind = metadata.bind
    
    setup_all(True)

    session.commit()

def main():
    initdb()
    #r1 = Record(name=u'入账1000', income=1000, category=u'A')
    #r2 = Record(name=u'刀具', outcome=150, category=u'B')
    #r3 = Record(name=u'买板', outcome=500, category=u'B')
    #r4 = Record(name=u'凳子', income=100, category=u'A')
    
    session.commit()

if __name__ == '__main__':
    main()
