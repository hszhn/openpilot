#include "selfdrive/ui/qt/widgets/prime.h"

#include <QDebug>
#include <QGridLayout>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QPushButton>
#include <QStackedWidget>
#include <QTimer>
#include <QVBoxLayout>

#include <QrCode.hpp>

#include "selfdrive/ui/qt/request_repeater.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/qt_window.h"
#include "selfdrive/ui/qt/widgets/wifi.h"

using qrcodegen::QrCode;

PairingQRWidget::PairingQRWidget(QWidget* parent) : QWidget(parent) {
  timer = new QTimer(this);
  connect(timer, &QTimer::timeout, this, &PairingQRWidget::refresh);
}

void PairingQRWidget::showEvent(QShowEvent *event) {
  refresh();
  timer->start(5 * 60 * 1000);
  device()->setOffroadBrightness(100);
}

void PairingQRWidget::hideEvent(QHideEvent *event) {
  timer->stop();
  device()->setOffroadBrightness(BACKLIGHT_OFFROAD);
}

void PairingQRWidget::refresh() {
  QString pairToken = CommaApi::create_jwt({{"pair", true}});
  QString qrString = (useKonikServer() ? "https://stable.konik.ai/?pair=" : "https://connect.comma.ai/?pair=") + pairToken;
  this->updateQrCode(qrString);
  update();
}

void PairingQRWidget::updateQrCode(const QString &text) {
  QrCode qr = QrCode::encodeText(text.toUtf8().data(), QrCode::Ecc::LOW);
  qint32 sz = qr.getSize();
  QImage im(sz, sz, QImage::Format_RGB32);

  QRgb black = qRgb(0, 0, 0);
  QRgb white = qRgb(255, 255, 255);
  for (int y = 0; y < sz; y++) {
    for (int x = 0; x < sz; x++) {
      im.setPixel(x, y, qr.getModule(x, y) ? black : white);
    }
  }

  // Integer division to prevent anti-aliasing
  int final_sz = ((width() / sz) - 1) * sz;
  img = QPixmap::fromImage(im.scaled(final_sz, final_sz, Qt::KeepAspectRatio), Qt::MonoOnly);
}

void PairingQRWidget::paintEvent(QPaintEvent *e) {
  QPainter p(this);
  p.fillRect(rect(), Qt::white);

  QSize s = (size() - img.size()) / 2;
  p.drawPixmap(s.width(), s.height(), img);
}


PairingPopup::PairingPopup(QWidget *parent) : DialogBase(parent) {
  QHBoxLayout *hlayout = new QHBoxLayout(this);
  hlayout->setContentsMargins(0, 0, 0, 0);
  hlayout->setSpacing(0);

  setStyleSheet("PairingPopup { background-color: #E0E0E0; }");

  // text
  QVBoxLayout *vlayout = new QVBoxLayout();
  vlayout->setContentsMargins(85, 70, 50, 70);
  vlayout->setSpacing(50);
  hlayout->addLayout(vlayout, 1);
  {
    QPushButton *close = new QPushButton(QIcon(":/icons/close.svg"), "", this);
    close->setIconSize(QSize(80, 80));
    close->setStyleSheet("border: none;");
    vlayout->addWidget(close, 0, Qt::AlignLeft);
    QObject::connect(close, &QPushButton::clicked, this, &QDialog::reject);

    vlayout->addSpacing(30);

    QLabel *title = new QLabel(tr("Pair your device to your %1 account").arg(useKonikServer() ? "Konik" : "comma"), this);
    title->setStyleSheet("font-size: 75px; color: black;");
    title->setWordWrap(true);
    vlayout->addWidget(title);

    QString serverUrl = useKonikServer() ? "stable.konik.ai" : "connect.comma.ai";

    QLabel *instructions = new QLabel(QString(R"(
      <ol type='1' style='margin-left: 15px;'>
        <li style='margin-bottom: 50px;'>%1</li>
        <li style='margin-bottom: 50px;'>%2</li>
        <li style='margin-bottom: 50px;'>%3</li>
      </ol>
    )").arg(tr("Go to https://%1 on your phone").arg(serverUrl))
    .arg(tr("Click \"add new device\" and scan the QR code on the right"))
    .arg(tr("Bookmark %1 to your home screen to use it like an app").arg(serverUrl)), this);

    instructions->setStyleSheet("font-size: 47px; font-weight: bold; color: black;");
    instructions->setWordWrap(true);
    vlayout->addWidget(instructions);

    vlayout->addStretch();
  }

  // QR code
  PairingQRWidget *qr = new PairingQRWidget(this);
  hlayout->addWidget(qr, 1);
}


PrimeUserWidget::PrimeUserWidget(QWidget *parent) : QFrame(parent) {
  setObjectName("primeWidget");
  QVBoxLayout *mainLayout = new QVBoxLayout(this);
  mainLayout->setContentsMargins(56, 40, 56, 40);
  mainLayout->setSpacing(20);

  QLabel *subscribed = new QLabel(tr("✓ SUBSCRIBED"));
  subscribed->setStyleSheet("font-size: 41px; font-weight: bold; color: #86FF4E;");
  mainLayout->addWidget(subscribed);

  QLabel *commaPrime = new QLabel(tr("comma prime"));
  commaPrime->setStyleSheet("font-size: 75px; font-weight: bold;");
  mainLayout->addWidget(commaPrime);
}


PrimeAdWidget::PrimeAdWidget(QWidget* parent) : QFrame(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(80, 90, 80, 60);
  main_layout->setSpacing(0);

  QLabel *upgrade = new QLabel(tr("Upgrade Now"));
  upgrade->setStyleSheet("font-size: 75px; font-weight: bold;");
  main_layout->addWidget(upgrade, 0, Qt::AlignTop);
  main_layout->addSpacing(50);

  QLabel *description = new QLabel(tr("Become a comma prime member at connect.comma.ai"));
  description->setStyleSheet("font-size: 56px; font-weight: light; color: white;");
  description->setWordWrap(true);
  main_layout->addWidget(description, 0, Qt::AlignTop);

  main_layout->addStretch();

  QLabel *features = new QLabel(tr("PRIME FEATURES:"));
  features->setStyleSheet("font-size: 41px; font-weight: bold; color: #E5E5E5;");
  main_layout->addWidget(features, 0, Qt::AlignBottom);
  main_layout->addSpacing(30);

  QVector<QString> bullets = {tr("Remote access"), tr("24/7 LTE connectivity"), tr("1 year of drive storage"), tr("Turn-by-turn navigation")};
  for (auto &b : bullets) {
    const QString check = "<b><font color='#465BEA'>✓</font></b> ";
    QLabel *l = new QLabel(check + b);
    l->setAlignment(Qt::AlignLeft);
    l->setStyleSheet("font-size: 50px; margin-bottom: 15px;");
    main_layout->addWidget(l, 0, Qt::AlignBottom);
  }

  setStyleSheet(R"(
    PrimeAdWidget {
      border-radius: 10px;
      background-color: #333333;
    }
  )");
}


SetupWidget::SetupWidget(QWidget* parent) : QFrame(parent) {
  QVBoxLayout *mainLayout = new QVBoxLayout(this);
  mainLayout->setContentsMargins(0, 0, 0, 0);
  mainLayout->setSpacing(30);

  auto addStatusCard = [=](const QString &title, const QVector<QPair<QString, QLabel **>> &rows) {
    QFrame *card = new QFrame(this);
    card->setObjectName("statusCard");
    QVBoxLayout *cardLayout = new QVBoxLayout(card);
    cardLayout->setContentsMargins(46, 30, 46, 30);
    cardLayout->setSpacing(12);

    QLabel *heading = new QLabel(title, card);
    heading->setProperty("type", "statusTitle");
    cardLayout->addWidget(heading);

    QGridLayout *grid = new QGridLayout;
    grid->setHorizontalSpacing(24);
    grid->setVerticalSpacing(10);
    for (int row = 0; row < rows.size(); ++row) {
      QLabel *name = new QLabel(rows[row].first, card);
      name->setProperty("type", "statusName");
      grid->addWidget(name, row, 0, Qt::AlignLeft);

      *rows[row].second = new QLabel("--", card);
      (*rows[row].second)->setProperty("type", "statusValue");
      grid->addWidget(*rows[row].second, row, 1, Qt::AlignRight);
    }
    grid->setColumnStretch(0, 1);
    cardLayout->addLayout(grid);
    mainLayout->addWidget(card, 1);
  };

  addStatusCard(tr("Vehicle Status"), {
    {tr("Vehicle"), &carRecognition},
    {tr("Control System"), &controlsReady},
  });
  addStatusCard(tr("Device Status"), {
    {tr("Temperature"), &deviceTemperature},
    {tr("Cooling Fan"), &fanStatus},
    {tr("Storage Available"), &storageStatus},
  });

  setStyleSheet(R"(
    #statusCard {
      border-radius: 8px;
      background-color: #333333;
    }
    QLabel[type="statusTitle"] { font-size: 44px; font-weight: 600; color: #E5E5E5; }
    QLabel[type="statusName"] { font-size: 36px; color: #A0A0A0; }
    QLabel[type="statusValue"] { font-size: 38px; font-weight: 500; }
  )");

  QTimer *statusTimer = new QTimer(this);
  QObject::connect(statusTimer, &QTimer::timeout, this, &SetupWidget::refreshStatus);
  statusTimer->start(1000);
  refreshStatus();
}

void SetupWidget::setStatus(QLabel *label, const QString &text, const QString &color) {
  label->setText(text);
  label->setStyleSheet("color: " + color + ";");
}

void SetupWidget::refreshStatus() {
  const SubMaster &sm = *uiState()->sm;
  const bool recognized = !params.get("CarParamsPersistent").empty();
  setStatus(carRecognition, recognized ? tr("2015 Buick Envision") : tr("Not Recognized"), recognized ? "#86FF4E" : "#FF6B6B");

  const bool controls_ready = params.getBool("ControlsReady");
  setStatus(controlsReady, controls_ready ? tr("Ready") : tr("Waiting for Vehicle"), controls_ready ? "#86FF4E" : "#F5C451");

  if (sm.alive("deviceState")) {
    const auto device_state = sm["deviceState"].getDeviceState();
    const int max_temp = qRound(device_state.getMaxTempC());
    const bool temp_warning = device_state.getThermalStatus() >= cereal::DeviceState::ThermalStatus::YELLOW;
    setStatus(deviceTemperature, QString::number(max_temp) + "°C", temp_warning ? "#FF6B6B" : "#86FF4E");
    setStatus(storageStatus, QString::number(qRound(device_state.getFreeSpacePercent())) + "%", "#FFFFFF");
  } else {
    setStatus(deviceTemperature, tr("Waiting for Data"), "#F5C451");
    setStatus(storageStatus, tr("Waiting for Data"), "#F5C451");
  }

  if (sm.alive("peripheralState")) {
    const int fan_rpm = sm["peripheralState"].getPeripheralState().getFanSpeedRpm();
    const int fan_request = sm.alive("deviceState") ? sm["deviceState"].getDeviceState().getFanSpeedPercentDesired() : 0;
    const bool fan_fault = fan_request > 0 && fan_rpm == 0;
    setStatus(fanStatus, fan_fault ? tr("FAULT - 0 RPM") : QString::number(fan_rpm) + " RPM", fan_fault ? "#FF6B6B" : "#86FF4E");
  } else {
    setStatus(fanStatus, tr("Waiting for Data"), "#F5C451");
  }
}
