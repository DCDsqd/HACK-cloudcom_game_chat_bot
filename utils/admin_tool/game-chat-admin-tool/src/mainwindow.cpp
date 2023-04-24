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

    ui->langBox->setStyleSheet(QssHelper::ReadRelativeQSS("languages_combo_box.qss"));
    ui->langBox->ensurePolished();

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
    addEventToLayout("Event name", "Event description", QDateTime::currentDateTime().addDays(1), 1, 0);
}

void MainWindow::addEventToLayout(const QString &name,
                                  const QString &descr,
                                  const QDateTime &date,
                                  const size_t duration,
                                  const size_t exp_reward)
{
    int cur_next_row = ui->eventsLayout->rowCount();

    // Event name
    QLineEdit* event_name = new QLineEdit(name);
    event_name->setFixedSize(EPI[E_NAME].sz);

    // Event description
    QTextEdit* event_descr = new QTextEdit(descr);
    event_descr->setFixedSize(EPI[E_DESCR].sz);

    // Event start time
    QDateTimeEdit *event_start_date = new QDateTimeEdit(date);
    event_start_date->setFixedSize(EPI[E_START].sz);
    event_start_date->setDisplayFormat("HH:mm dd-MM-yy");

    // Event duration
    QLineEdit* event_dur = new QLineEdit(QString::number(duration));
    event_dur->setFixedSize(EPI[E_DUR].sz);
    event_dur->setValidator(new QIntValidator(1, mins_in_year, this));

    // Event experience reward
    QLineEdit* event_exp_reward = new QLineEdit(QString::number(exp_reward));
    event_exp_reward->setFixedSize(EPI[E_EXP].sz);
    event_exp_reward->setValidator(new QIntValidator(0, event_exp_reward_upper_limit, this));

    // Delete event button
    QPushButton* event_delete = new QPushButton(tr("Delete!"));
    event_delete->setFixedSize(EPI[E_DEL].sz);
    QObject::connect(event_delete, &QPushButton::clicked, this, [this, cur_next_row]{
        GridLayoutUtil::removeRow(ui->eventsLayout, cur_next_row);
        //deleteRowFromLayout(cur_next_row);
    });
    event_delete->setStyleSheet(QssHelper::ReadRelativeQSS("evil_push_button.qss"));
    event_delete->ensurePolished();

    // Adding events to grid layout
    ui->eventsLayout->addWidget(event_name, cur_next_row, E_NAME, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_descr, cur_next_row, E_DESCR, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_start_date, cur_next_row, E_START, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_dur, cur_next_row, E_DUR, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_exp_reward, cur_next_row, E_EXP, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_delete, cur_next_row, E_DEL, Qt::AlignCenter);

    //current_translatable_widgets.insert({event_name, "QLineEdit"});
    //current_translatable_widgets.insert({event_descr, "QTextEdit"});
    current_translatable_widgets->insert(new WidgetHolder{event_delete, "QPushButton", "Delete!"});

    //Scroll down to be able to see a newly added widget
    ui->scrollArea->verticalScrollBar()->setValue(ui->scrollArea->verticalScrollBar()->maximumHeight());
    //ui->scrollArea->ensureWidgetVisible(eventName, 100, 100);
}

void MainWindow::addEventToLayout(const Event &event)
{
    addEventToLayout(event.name,
                     event.description,
                     event.start_date,
                     event.duration,
                     event.exp_reward);
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
            WidgetHolder* tmp_widget_holder_for_cmp = new WidgetHolder(itemWidget);
            auto it = current_translatable_widgets->find(tmp_widget_holder_for_cmp);
            delete tmp_widget_holder_for_cmp;
            if(it != current_translatable_widgets->end()){
                current_translatable_widgets->erase(it);
                qDebug() << "Was not able to find widget that needs to be deleted in current_translatable_widgets, "
                            "itemWidget = " << itemWidget;
            }
            delete itemWidget;
        }
    }
    ui->eventsLayout->update();
}

void MainWindow::clearLayout()
{
    for(int i = 0; i < ui->eventsLayout->rowCount(); ++i){
        GridLayoutUtil::removeRow(ui->eventsLayout, i);
    }
    current_translatable_widgets->clear();
    //ClearLay(ui->eventsLayout);
}

void MainWindow::insertHeadersIntoLayout()
{
    int cur_next_row = ui->eventsLayout->rowCount();

    // Event name
    QLabel* event_name = new QLabel(tr("Name"));
    event_name->setFixedSize(EPI[E_NAME].sz);

    // Event description
    QLabel* event_descr = new QLabel(tr("Description"));
    event_descr->setFixedSize(EPI[E_DESCR].sz);

    // Event start time
    QLabel *event_start_date = new QLabel(tr("Start time"));
    event_start_date->setFixedSize(EPI[E_START].sz);

    // Event duration
    QLabel* event_dur = new QLabel(tr("Duration\n (mins)"));
    event_dur->setFixedSize(EPI[E_DUR].sz);

    // Event experience reward
    QLabel* event_exp_reward = new QLabel(tr("Exp rew."));
    event_exp_reward->setFixedSize(EPI[E_EXP].sz);

    // Delete event button
    QLabel* event_delete = new QLabel(tr("Delete buttons"));
    event_delete->setFixedSize(EPI[E_DEL].sz);

    // Adding events to grid layout
    ui->eventsLayout->addWidget(event_name, cur_next_row, E_NAME, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_descr, cur_next_row, E_DESCR, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_start_date, cur_next_row, E_START, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_dur, cur_next_row, E_DUR, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_exp_reward, cur_next_row, E_EXP, Qt::AlignCenter);
    ui->eventsLayout->addWidget(event_delete, cur_next_row, E_DEL, Qt::AlignCenter);

    current_translatable_widgets->insert(new WidgetHolder{event_name, "QLabel", "Name"});
    current_translatable_widgets->insert(new WidgetHolder{event_descr, "QLabel", "Description"});
    current_translatable_widgets->insert(new WidgetHolder{event_start_date, "QLabel", "Start time"});
    current_translatable_widgets->insert(new WidgetHolder{event_dur, "QLabel", "Duration\n (mins)"});
    current_translatable_widgets->insert(new WidgetHolder{event_exp_reward, "QLabel", "Exp rew."});
    current_translatable_widgets->insert(new WidgetHolder{event_delete, "QLabel", "Delete buttons"});
}

void MainWindow::loadEventsFromDb()
{
    insertHeadersIntoLayout();
    const QVector<Event> events = db->SelectEvents(default_events_table_name);
    for(const auto& event : events) {
        addEventToLayout(event);
    }
}

QVector<Event> MainWindow::getCurrentEventsList() const
{
    QVector<Event> event_list;

    for(size_t i = 2; i < (size_t)ui->eventsLayout->rowCount(); ++i){
        Event cur_event;

        //QGridLayout* lay = ui->eventsLayout; // for debug purposes since ui->eventsLayout is not visible for debugger smh
        auto item = ui->eventsLayout->itemAtPosition(i, 0);
        if(!item){
            continue;
        }
        QWidget* name_widget = item->widget();
        // Skip headers
        /*
        if(name_widget->metaObject()->className() == std::string("QLabel").c_str()){
            continue;
        }
        */
        if([[maybe_unused]] QLabel* tmp_label = qobject_cast<QLabel*>(name_widget)){
            //delete tmp_label;
            continue;
        }
        QWidget* descr_widget = ui->eventsLayout->itemAtPosition(i, 1)->widget();
        QWidget* date_widget = ui->eventsLayout->itemAtPosition(i, 2)->widget();
        QWidget* duration_widget = ui->eventsLayout->itemAtPosition(i, 3)->widget();
        QWidget* exp_widget = ui->eventsLayout->itemAtPosition(i, 4)->widget();

        QLineEdit* casted_name = qobject_cast<QLineEdit*>(name_widget);
        QTextEdit* casted_descr = qobject_cast<QTextEdit*>(descr_widget);
        QDateTimeEdit* casted_start_date = qobject_cast<QDateTimeEdit*>(date_widget);
        QLineEdit* casted_duration = qobject_cast<QLineEdit*>(duration_widget);
        QLineEdit* casted_exp = qobject_cast<QLineEdit*>(exp_widget);

        cur_event.name = casted_name->text();
        cur_event.description = casted_descr->toPlainText();
        cur_event.start_date = casted_start_date->dateTime();
        cur_event.duration = casted_duration->text().toUInt();
        cur_event.exp_reward = casted_exp->text().toUInt();

        event_list.push_back(cur_event);
    }

    return event_list;
}

QVector<EventPlacementData> MainWindow::constructEventPlacementData()
{
    return
    {
        {E_NAME, 130, 35},
        {E_DESCR, 130, 100},
        {E_START, 130, 30},
        {E_DUR, 80, 30},
        {E_EXP, 80, 30},
        {E_DEL, 100, 50}
    };
}

void MainWindow::changeEvent(QEvent *event)
{
    if(QEvent::LanguageChange == event->type())
    {
        ui->retranslateUi(this);
        reTranslateNonUiWidgets();
    }
}

void MainWindow::reTranslateNonUiWidgets()
{
    for(auto& widget_holder : *current_translatable_widgets){
        QByteArray tmp_byte_array = widget_holder->text.toLocal8Bit();
        const char* original_text = tmp_byte_array.data();
        if(widget_holder->type == "QLabel"){
            QLabel* label = static_cast<QLabel*>(widget_holder->widget);
            label->setText(tr(original_text));
        }
        else if(widget_holder->type == "QLineEdit"){
            QLineEdit* line = static_cast<QLineEdit*>(widget_holder->widget);
            line->setText(tr(original_text));
        }
        else if(widget_holder->type == "QTextEdit"){
            QTextEdit* text = static_cast<QTextEdit*>(widget_holder->widget);
            text->setText(tr(original_text));
        }
        else if(widget_holder->type == "QPushButton"){
            QPushButton* button = static_cast<QPushButton*>(widget_holder->widget);
            button->setText(tr(original_text));
        }
        else{
            qDebug() << "Unknown type = " << widget_holder->type << " in reTranslateNonUiWidgets(). Widget was not translated.";
        }
    }
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
            WidgetHolder* tmp_widget_holder_for_cmp = new WidgetHolder(curItem->widget());
            auto it = current_translatable_widgets->find(tmp_widget_holder_for_cmp);
            delete tmp_widget_holder_for_cmp;
            if(it != current_translatable_widgets->end()){
                current_translatable_widgets->erase(it);
            }
            else{
                qDebug() << "Was not able to find widget that needs to be deleted in current_translatable_widgets, "
                            "curItem->widget() = " << curItem->widget();
            }
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

void MainWindow::SetLang(QString ts_file_path)
{
    if(!translator->load(ts_file_path, qApp->applicationDirPath())){
        qDebug() << "Failed to set language with the ts_file_path = " << ts_file_path << ". Aborting.";
        return;
    }
    qApp->installTranslator(translator);
}

void MainWindow::on_langBox_currentIndexChanged([[maybe_unused]] int index)
{
    SetLang("game-chat-admin-tool_" + ui->langBox->currentText());
}

