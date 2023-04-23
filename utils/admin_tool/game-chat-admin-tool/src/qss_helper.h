#ifndef QSSHELPER_H
#define QSSHELPER_H

#include <QString>
#include <QFile>
#include <QDebug>

#define DEFAULT_QSS_RESOURCE_PATH "../game-chat-admin-tool/res/qss/"

class QssHelper
{
public:
    QssHelper() = delete;

    static QString ReadQSS(QString file_path);
    static QString ReadRelativeQSS(QString file_rel_path);

};

#endif // QSSHELPER_H
