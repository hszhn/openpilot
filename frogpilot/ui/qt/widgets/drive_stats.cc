#include "frogpilot/ui/qt/widgets/drive_stats.h"

#include <QDate>
#include <QJsonDocument>
#include <QJsonObject>

static QLabel *newLabel(const QString &text, const QString &type) {
  QLabel *label = new QLabel(text);
  label->setProperty("type", type);
  return label;
}

DriveStats::DriveStats(QWidget *parent) : QFrame(parent) {
  isMetric = params.getBool("IsMetric");

  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 25, 50, 20);

  addStatsLayouts(tr("ALL TIME"), all, true);
  addStatsLayouts(tr("PAST WEEK"), week);

  setStyleSheet(R"(
    DriveStats {
      background-color: #333333;
      border-radius: 10px;
    }

    QLabel[type="frogpilot_title"] { font-size: 50px; font-weight: 500; color: #178643; }
    QLabel[type="number"] { font-size: 65px; font-weight: 400; }
    QLabel[type="title"] { font-size: 50px; font-weight: 500; }
    QLabel[type="unit"] { font-size: 50px; font-weight: 300; color: #A0A0A0; }
  )");
}

void DriveStats::showEvent(QShowEvent *event) {
  isMetric = params.getBool("IsMetric");

  updateStats();
}

void DriveStats::addStatsLayouts(const QString &title, StatsLabels &labels, bool FrogPilot) {
  QGridLayout *grid_layout = new QGridLayout;
  grid_layout->setVerticalSpacing(10);
  grid_layout->setContentsMargins(0, 10, 0, 10);

  int row = 0;
  grid_layout->addWidget(newLabel(title, FrogPilot ? "frogpilot_title" : "title"), row++, 0, 1, 3);
  grid_layout->addItem(new QSpacerItem(0, 10), row++, 0, 1, 1);

  grid_layout->addWidget(labels.routes = newLabel("0", "number"), row, 0, Qt::AlignLeft);
  grid_layout->addWidget(labels.distance = newLabel("0", "number"), row, 1, Qt::AlignLeft);
  grid_layout->addWidget(labels.hours = newLabel("0", "number"), row, 2, Qt::AlignLeft);

  grid_layout->addWidget(newLabel(tr("Drives"), "unit"), row + 1, 0, Qt::AlignLeft);
  grid_layout->addWidget(labels.distance_unit = newLabel(isMetric ? tr("KM") : tr("Miles"), "unit"), row + 1, 1, Qt::AlignLeft);
  grid_layout->addWidget(newLabel(tr("Hours"), "unit"), row + 1, 2, Qt::AlignLeft);

  QVBoxLayout *main_layout = static_cast<QVBoxLayout *>(layout());
  main_layout->addLayout(grid_layout);
  main_layout->addStretch(1);
}

void DriveStats::updateStatsForLabel(double routes, double meters, double seconds, StatsLabels &labels) {
  labels.distance->setText(QString::number(int(meters * (isMetric ? 0.001 : METER_TO_MILE))));
  labels.distance_unit->setText(isMetric ? tr("KM") : tr("Miles"));
  labels.hours->setText(QString::number(int(seconds / (60 * 60))));
  labels.routes->setText(QString::number(int(routes)));
}

void DriveStats::updateStats() {
  const QJsonObject stats = QJsonDocument::fromJson(QByteArray::fromStdString(params.get("FrogPilotStats"))).object();

  const double total_routes = stats.contains("FrogPilotDrives") ? stats.value("FrogPilotDrives").toDouble() : params.getInt("FrogPilotDrives");
  const double total_meters = stats.contains("FrogPilotMeters") ? stats.value("FrogPilotMeters").toDouble() : params.getFloat("FrogPilotKilometers") * 1000;
  const double total_seconds = stats.contains("FrogPilotSeconds") ? stats.value("FrogPilotSeconds").toDouble() : params.getFloat("FrogPilotMinutes") * 60;
  updateStatsForLabel(total_routes, total_meters, total_seconds, all);

  double week_routes = 0;
  double week_meters = 0;
  double week_seconds = 0;
  const QDate cutoff = QDate::currentDate().addDays(-6);
  const QJsonObject daily_stats = stats.value("DailyDriveStats").toObject();
  for (auto it = daily_stats.constBegin(); it != daily_stats.constEnd(); ++it) {
    const QDate date = QDate::fromString(it.key(), Qt::ISODate);
    if (date.isValid() && date >= cutoff) {
      const QJsonObject day = it.value().toObject();
      week_routes += day.value("drives").toDouble();
      week_meters += day.value("meters").toDouble();
      week_seconds += day.value("seconds").toDouble();
    }
  }
  updateStatsForLabel(week_routes, week_meters, week_seconds, week);
}
