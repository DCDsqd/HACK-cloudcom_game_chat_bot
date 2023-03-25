QT += core gui network sql

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++17
CONFIG += lrelease
CONFIG += embed_translations

SOURCES += \
    src/main.cpp \
    src/mainwindow.cpp \
    src/translatorwrapper.cpp

HEADERS += \
    src/mainwindow.h \
    src/translatorwrapper.h

FORMS += \
    ui/mainwindow.ui

TRANSLATIONS += \
    ts/game-chat-admin-tool_ru_RU.ts

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target
