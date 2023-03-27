QT += core gui network sql

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++17
CONFIG += lrelease
CONFIG += embed_translations

SOURCES += \
    src/database.cpp \
    src/event.cpp \
    src/main.cpp \
    src/mainwindow.cpp \
    src/translator_wrapper.cpp

HEADERS += \
    src/database.h \
    src/event.h \
    src/mainwindow.h \
    src/translator_wrapper.h

FORMS += \
    ui/mainwindow.ui

TRANSLATIONS += \
    ts/game-chat-admin-tool_ru_RU.ts

qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

RESOURCES += \
    res/qrc/qss_files.qrc
