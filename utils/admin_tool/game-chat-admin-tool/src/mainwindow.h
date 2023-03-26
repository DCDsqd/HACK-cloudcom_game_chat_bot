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
#include <QDate>
#include <QTime>

#include <memory>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void on_addEventButton_clicked();

private: //functions
    void addEventToLayout();
    void addEventToLayout(const QString& name, const QString& descr, const QDate& date, const size_t duration);
    void addEventToLayout(const Event& event);
    void loadEventsFromDb();

private: //fields
    Ui::MainWindow *ui;
    std::unique_ptr<Database> db = nullptr;
    static constexpr int mins_in_year = 525600;
    const QString default_events_table_name = "global_events";
};
#endif // MAINWINDOW_H
