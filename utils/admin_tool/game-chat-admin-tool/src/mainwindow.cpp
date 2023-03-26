#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    db = std::make_unique<Database>();
    db->SetupConnection("../../../db/database.db"); // Path should be kept relative to build dir!

    ui->mainStackedWidget->setCurrentIndex(1);
    ui->scrollAreaWidgetContents->setLayout(ui->eventsLayout);

    loadEventsFromDb();
}

MainWindow::~MainWindow()
{
    delete ui;
}


void MainWindow::on_addEventButton_clicked()
{
    addEventToLayout();
}

void MainWindow::addEventToLayout()
{
    addEventToLayout("Event name", "Event description", QDateTime::currentDateTime().addDays(1), 1);
}

void MainWindow::addEventToLayout(const QString &name, const QString &descr, const QDateTime &date, const size_t duration)
{
    int cur_next_row = ui->eventsLayout->rowCount();

    // Event name
    QLineEdit* event_name = new QLineEdit(name);
    event_name->setFixedSize(QSize(100, 50));

    // Event description
    QTextEdit* event_descr = new QTextEdit(descr);
    event_descr->setFixedSize(QSize(100, 100));

    // Event start time
    QDateTimeEdit *event_start_date = new QDateTimeEdit(date);
    //event_start_date->setFixedSize(480, 30);
    event_start_date->setDisplayFormat("HH:mm dd-MM-yy");

    // Event duration
    QLineEdit* event_dur = new QLineEdit(QString::number(duration));
    event_dur->setFixedSize(QSize(100, 30));
    event_dur->setValidator(new QIntValidator(1, mins_in_year, this));

    // Delete event button
    QPushButton* event_delete = new QPushButton("Delete!");
    event_delete->setFixedSize(100, 50);
    QObject::connect(event_delete, &QPushButton::clicked, this, [this, cur_next_row]{
        deleteRowFromLayout(cur_next_row);
    });

    // Adding events to grid layout
    ui->eventsLayout->addWidget(event_name, cur_next_row, 0, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_descr, cur_next_row, 1, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_start_date, cur_next_row, 2, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_dur, cur_next_row, 3, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_delete, cur_next_row, 4, Qt::AlignCenter);

    //Scroll down to be able to see a newly added widget
    ui->scrollArea->verticalScrollBar()->setValue(ui->scrollArea->verticalScrollBar()->maximumHeight());
    //ui->scrollArea->ensureWidgetVisible(eventName, 100, 100);
}

void MainWindow::addEventToLayout(const Event &event)
{
    addEventToLayout(event.name,
                     event.description,
                     event.start_date,
                     event.duration);
}

void MainWindow::deleteRowFromLayout(size_t row)
{
    for(int c = 0; c < ui->eventsLayout->columnCount(); ++c)
    {
        QLayoutItem* item = ui->eventsLayout->itemAtPosition( row, c );
        QWidget* itemWidget = item->widget();
        if(itemWidget)
        {
            ui->eventsLayout->removeWidget(itemWidget);
            delete itemWidget;
        }
    }
    ui->eventsLayout->update();
}

void MainWindow::clearLayout()
{
    ClearLay(ui->eventsLayout);
}

void MainWindow::loadEventsFromDb()
{
    const QVector<Event> events = db->SelectEvents(default_events_table_name);
    for(const auto& event : events) {
        addEventToLayout(event);
    }
}

QVector<Event> MainWindow::getCurrentEventsList() const
{
    QVector<Event> event_list;

    for(size_t i = 1; i < (size_t)ui->eventsLayout->rowCount(); ++i){
        Event cur_event;

        QWidget* name_widget = ui->eventsLayout->itemAtPosition(i, 0)->widget();
        QWidget* descr_widget = ui->eventsLayout->itemAtPosition(i, 1)->widget();
        QWidget* date_widget = ui->eventsLayout->itemAtPosition(i, 2)->widget();
        QWidget* duration_widget = ui->eventsLayout->itemAtPosition(i, 3)->widget();

        QLineEdit* casted_name = static_cast<QLineEdit*>(name_widget);
        QTextEdit* casted_descr = static_cast<QTextEdit*>(descr_widget);
        QDateTimeEdit* casted_start_date = static_cast<QDateTimeEdit*>(date_widget);
        QLineEdit* casted_duration = static_cast<QLineEdit*>(duration_widget);

        cur_event.name = casted_name->text();
        cur_event.description = casted_descr->toPlainText();
        cur_event.start_date = casted_start_date->dateTime();
        cur_event.duration = casted_duration->text().toUInt();

        event_list.push_back(cur_event);
    }

    return event_list;
}


void MainWindow::on_saveAllButton_clicked()
{
    // @TODO: Perhaps make a popup dialog asking for confirmation of this action
    db->OverwriteEventsInfo(default_events_table_name, getCurrentEventsList());
    // @TODO: Perhaps make a popup dialog informing that action has ended + its status (?)
}


void MainWindow::on_reloadDataButton_clicked()
{
    // Delete widgets from prev layout
    // delete ui->eventsLayout;
    //ui->eventsLayout = new QGridLayout();
    clearLayout();
    loadEventsFromDb();
}

void MainWindow::ClearLay(QGridLayout *lay)
{
    if(lay == nullptr){
        return;
    }
    QLayoutItem* curItem;
    //qDebug() << "Entered ClearLay() with lay consist of " << lay->count() << " items";
    while(lay->count()){
        curItem = lay->takeAt(0);
        if(curItem == nullptr){
            continue;
        }
        //qDebug() << "Entered while, i = " << i;
        if(curItem->layout() != nullptr){
            ClearLay(dynamic_cast<QGridLayout*>(curItem->layout()));
            //qDebug() << "Deleted lay: " << curItem->layout();
            //TO DO: Figure out if following line leads to memory leak or is it supposed to work like that
            //delete curItem->layout();
        }
        else if(curItem->widget() != nullptr){
            //qDebug() << "Deleted widget: " << curItem->widget() << " i = " << i;
            curItem->widget()->hide();
            //curItem->widget()->deleteLater();
            delete curItem->widget();
        }
        //qDebug() << "Trying to delete item: " << curItem;
        //else {
        // @TODO: Figure out if following line leads to memory leak or is it supposed to work like that
        //delete curItem;
        //}
    }
    //qDebug() << "ClearLay() finished working";
}
