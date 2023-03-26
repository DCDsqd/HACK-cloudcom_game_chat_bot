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

    static void PrintSqlExecInfoIfErr(QSqlQuery &query);
    static void PrintSqlExecInfo(QSqlQuery &query);
private:
    std::unique_ptr<QSqlDatabase> db = nullptr;
};

#endif // DATABASE_H
