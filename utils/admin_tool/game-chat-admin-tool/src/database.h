#ifndef DATABASE_H
#define DATABASE_H

#include "event.h"

#include <QSqlDatabase>
#include <QDebug>
#include <QSqlError>
#include <QSqlQuery>
#include <QVector>

#include <memory>

class Database
{
public:
    Database();
    ~Database();

    void SetupConnection(const QString &dbPath, const QString &connectionName = "default");
    bool IsConnected() const;
    QVector<Event> SelectEvents(const QString &table_name) const;
    void DeleteEventsInfo(const QString &table_name) const;
    void OverwriteEventsInfo(const QString &table_name, const QVector<Event> &events) const;
    void InsertEventIntoDb(const QString &table_name, const Event& event) const;

    static void PrintSqlExecInfoIfErr(QSqlQuery &query);
    static void PrintSqlExecInfo(QSqlQuery &query);

private: // functions
    void SaveEventsInfo(const QString &table_name, const QVector<Event> &events) const;

private: // fields
    std::unique_ptr<QSqlDatabase> db = nullptr;
};

#endif // DATABASE_H
