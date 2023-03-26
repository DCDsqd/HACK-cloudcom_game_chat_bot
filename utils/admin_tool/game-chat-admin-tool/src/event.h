#ifndef EVENT_H
#define EVENT_H

#include <QString>
#include <QDate>

class Event
{
public:
    Event();
    ~Event();

    QString name = "";
    QString description = "";
    QDate start_date = QDate::currentDate().addDays(1);
    size_t duration = 1; // in mins
};

#endif // EVENT_H
