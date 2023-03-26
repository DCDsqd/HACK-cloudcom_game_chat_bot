#include "translator_wrapper.h"

TranslatorWrapper::TranslatorWrapper(QApplication &app_) : app(app_)
{

}

void TranslatorWrapper::initAndBindTranslator()
{
    QTranslator translator;
    const QStringList uiLanguages = QLocale::system().uiLanguages();
    for (const QString &locale : uiLanguages) {
        const QString baseName = "game-chat-admin-tool_" + QLocale(locale).name();
        if (translator.load(":/i18n/" + baseName)) {
            app.installTranslator(&translator);
            break;
        }
    }
}
