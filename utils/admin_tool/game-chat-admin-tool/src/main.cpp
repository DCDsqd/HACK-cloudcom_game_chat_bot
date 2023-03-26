#include "mainwindow.h"
#include "translator_wrapper.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    TranslatorWrapper translator(app);
    translator.initAndBindTranslator();
    MainWindow window;
    window.show();
    return app.exec();
}
