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
    src/qss_helper.cpp

HEADERS += \
    src/database.h \
    src/event.h \
    src/grid_layout_util.h \
    src/mainwindow.h \
    src/qss_helper.h \
    src/widget_holder.h

FORMS += \
    ui/mainwindow.ui

TRANSLATIONS += \
    ts/game-chat-admin-tool_Russian.ts \
    ts/game-chat-admin-tool_English.ts

qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

RESOURCES += \
    res/qrc/icons.qrc \
    res/qrc/langs.qrc \
    res/qrc/qss_files.qrc

QMAKE_POST_LINK = lrelease game-chat-admin-tool.pro


#LANGUAGES = ru
#
## parameters: var, prepend, append
#defineReplace(prependAll) {
#     for(a,$$1):result += $$2$${a}$$3
#     return($$result)
#}
#
#TRANSLATIONS = $$prependAll(LANGUAGES, $$PWD/ts/game-chat-admin-tool_, .ts)
#
#TRANSLATIONS_FILES =
#
#qtPrepareTool(LRELEASE, lrelease)
#for(tsfile, TRANSLATIONS) {
#     qmfile = $$shadowed($$tsfile)
#     qmfile ~= s,.ts$,.qm,
#     qmdir = $$dirname(qmfile)
#     !exists($$qmdir) {
#     mkpath($$qmdir)|error("Aborting.")
#     }
#     command = $$LRELEASE -removeidentical $$tsfile -qm $$qmfile
#     system($$command)|error("Failed to run: $$command")
#     TRANSLATIONS_FILES += $$qmfile
#}
#
#wd = $$replace(PWD, /, $$QMAKE_DIR_SEP)
