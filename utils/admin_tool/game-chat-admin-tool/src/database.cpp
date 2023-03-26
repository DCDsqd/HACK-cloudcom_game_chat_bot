#include "database.h"

Database::Database()
{

}

Database::~Database()
{

}

void Database::SetupConnection(const QString& dbPath, const QString& connectionName)
{
    db = std::make_unique<QSqlDatabase>(QSqlDatabase::addDatabase("QSQLITE", connectionName));
    db->setDatabaseName(dbPath);
    if(!db->open()){
        qDebug() << "Database failed to open with given path: " << dbPath << "! Error: " << db->lastError().text();
    }
    else{
        qDebug() << "Database was successfuly opened!";
    }
}

bool Database::IsConnected() const
{
    return db == nullptr;
}

QVector<Event> Database::SelectEvents(const QString &table_name) const
{
    QVector<Event> event_list;

    QSqlQuery query(*db);
    query.exec("SELECT * FROM " + table_name + ";");
    Database::PrintSqlExecInfoIfErr(query);
    while(query.next()){
        Event cur_event;
        cur_event.name = query.value(1).toString();
        cur_event.description = query.value(2).toString();
        auto raw = query.value(3).toString();
        cur_event.start_date = QDateTime::fromString(raw, "yyyy-MM-dd hh:mm:ss");
        cur_event.duration = query.value(4).toUInt();
        event_list.push_back(cur_event);
    }

    return event_list;
}

void Database::PrintSqlExecInfoIfErr(QSqlQuery &query)
{
    if(query.lastError().isValid()){
        PrintSqlExecInfo(query);
    }
}

void Database::PrintSqlExecInfo(QSqlQuery &query)
{
    qDebug() << query.executedQuery() << " . Error: " << query.lastError().text();
}

void Database::DeleteEventsInfo(const QString& table_name) const
{
    QSqlQuery query(*db);
    QString queryStatement = "DELETE FROM " + table_name;
    query.exec(queryStatement);
    PrintSqlExecInfoIfErr(query);
}

void Database::OverwriteEventsInfo(const QString &table_name, const QVector<Event> &events) const
{
    DeleteEventsInfo(table_name);
    SaveEventsInfo(table_name, events);
}

void Database::InsertEventIntoDb(const QString& table_name, const Event &event) const
{
    QSqlQuery query(*db);
    QString queryStatement = "INSERT INTO " + table_name +
            " (name, descr, start_time, duration) " +
            " VALUES('" +
            event.name + "', '" +
            event.description + "', '" +
            event.start_date.toString("yyyy-MM-dd hh:mm:ss") + "', '" +
            QString::number(event.duration) + "');";
    query.exec(queryStatement);
    PrintSqlExecInfoIfErr(query);
}

void Database::SaveEventsInfo(const QString &table_name, const QVector<Event>& events) const
{
    for(const auto& event : events){
        InsertEventIntoDb(table_name, event);
    }
}
