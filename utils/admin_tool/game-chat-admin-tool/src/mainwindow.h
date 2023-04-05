#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include "database.h"

#include <QMainWindow>
#include <QGridLayout>
#include <QLayout>
#include <QPushButton>
#include <QLabel>
#include <QScrollArea>
#include <QScrollBar>
#include <QDateTimeEdit>
#include <QLineEdit>
#include <QValidator>
#include <QString>
#include <QDate>
#include <QTime>
#include <QTranslator>
#include <QSet>
#include <QEvent>
#include <QMap>
#include <QDir>
#include <QLocale>
#include <QApplication>

#include <memory>
#include <map>

#define EPI event_placement_info // for shorter name usage

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

    void ClearLay(QGridLayout *lay);
    void SetLang(QString ts_file_path);
private slots:
    void on_addEventButton_clicked();

    void on_saveAllButton_clicked();

    void on_reloadDataButton_clicked();

    void on_langBox_currentIndexChanged(int index);

private: //functions
    void addEventToLayout();
    void addEventToLayout(const QString& name,
                          const QString& descr,
                          const QDateTime &date,
                          const size_t duration,
                          const size_t exp_reward);
    void addEventToLayout(const Event& event);
    void deleteRowFromLayout(size_t row);
    void clearLayout();
    void insertHeadersIntoLayout();
    void loadEventsFromDb();
    QVector<Event> getCurrentEventsList() const;
    void changeEvent(QEvent* event);
    void reTranslateNonUiWidgets();

    static QVector<EventPlacementData> constructEventPlacementData();

private: //fields
    Ui::MainWindow *ui;
    std::unique_ptr<Database> db = nullptr;
    static constexpr int mins_in_year = 525600;
    static constexpr int event_exp_reward_upper_limit = 200000;
    const QString default_events_table_name = "global_events";
    const QVector<EventPlacementData> event_placement_info = constructEventPlacementData();
    std::map<QWidget*, std::pair<QString, QString>> current_translatable_widgets;
    QTranslator* translator = new QTranslator();
};
#endif // MAINWINDOW_H
