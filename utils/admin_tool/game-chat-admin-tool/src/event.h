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
    QDateTime start_date = QDateTime::currentDateTime().addDays(1);
    size_t duration = 1; // in mins
    size_t exp_reward = 0;
};

#endif // EVENT_H
