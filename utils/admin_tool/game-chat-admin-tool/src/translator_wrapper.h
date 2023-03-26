#ifndef TRANSLATOR_WRAPPER_H
#define TRANSLATOR_WRAPPER_H

#include <QString>
#include <QTranslator>
#include <QLocale>
#include <QApplication>

class TranslatorWrapper
{
public:
    TranslatorWrapper() = delete;
    TranslatorWrapper(QApplication& app_);
    ~TranslatorWrapper() = default;

    void initAndBindTranslator();
private:
    QApplication& app;
};

#endif // TRANSLATOR_WRAPPER_H
