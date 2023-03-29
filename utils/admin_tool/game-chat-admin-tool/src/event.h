#ifndef EVENT_H
#define EVENT_H

#include <QString>
#include <QDate>
#include <QSize>

#define E_NAME 0
#define E_DESCR 1
#define E_START 2
#define E_DUR 3
#define E_EXP 4
#define E_DEL 5

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

class EventPlacementData
{
public:
    EventPlacementData();
    ~EventPlacementData();

    EventPlacementData(int idx_, size_t h_, size_t w_);

    int idx = -1;
    size_t h = 0;
    size_t w = 0;
    QSize sz = {0, 0};
};

#endif // EVENT_H
