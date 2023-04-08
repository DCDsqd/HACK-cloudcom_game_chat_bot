#ifndef WIDGET_HOLDER_H
#define WIDGET_HOLDER_H

#include <QString>
#include <QWidget>

struct WidgetHolder{

    QWidget* widget = nullptr;
    QString type = "unknown";
    QString text = "";

    WidgetHolder() = default;
    WidgetHolder(QWidget* w) : widget(w){};
    WidgetHolder(QWidget* w, const QString& type_, const QString text_) : widget(w), type(type_), text(text_){};
    ~WidgetHolder()
    {
        delete widget;
    }

    bool operator=(const WidgetHolder& oth) const
    {
        return widget == oth.widget;
    }
    bool operator=(const QWidget* oth_widget) const
    {
        return widget == oth_widget;
    }
    bool operator<(const WidgetHolder& oth) const
    {
        return widget < oth.widget;
    }
};

#endif // WIDGET_HOLDER_H
