#include "qss_helper.h"

QString QssHelper::ReadQSS(QString file_path)
{
    QFile file(file_path);
    QString qss = file.readAll();
    file.close();
    return qss;
}

QString QssHelper::ReadRelativeQSS(QString file_rel_path)
{
    return ReadQSS(DEFAULT_QSS_RESOURCE_PATH + file_rel_path);
}
