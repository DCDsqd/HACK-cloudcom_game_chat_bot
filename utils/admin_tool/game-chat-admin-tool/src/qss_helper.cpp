#include "qss_helper.h"

QString QssHelper::ReadQSS(QString file_path)
{
    QFile file(file_path);
    if(!file.open(QIODevice::ReadOnly)) {
        qDebug() << file.errorString();
    }
    QString qss = QLatin1String(file.readAll());
    file.close();
    return qss;
}

QString QssHelper::ReadRelativeQSS(QString file_rel_path)
{
    return ReadQSS(DEFAULT_QSS_RESOURCE_PATH + file_rel_path);
}
