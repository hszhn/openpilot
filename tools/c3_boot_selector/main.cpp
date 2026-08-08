#include <QApplication>
#include <QFile>
#include <QFont>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QTimer>
#include <QVBoxLayout>
#include <QWidget>

namespace {
constexpr int kStableExitCode = 10;
constexpr int kLegacyExitCode = 20;
constexpr int kTimeoutSeconds = 10;

QString readActiveVersion() {
  QFile state_file("/data/c3_boot_selector/active_version");
  if (state_file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    return QString::fromUtf8(state_file.readAll()).trimmed();
  }
  return "stable";
}
}  // namespace

int main(int argc, char *argv[]) {
  QApplication app(argc, argv);
  QWidget window;
  window.setWindowFlags(Qt::FramelessWindowHint);
  window.setStyleSheet("background: #101418; color: white;");

  auto *layout = new QVBoxLayout(&window);
  layout->setContentsMargins(120, 90, 120, 90);
  layout->setSpacing(44);

  auto *title = new QLabel(QStringLiteral("选择启动系统"));
  title->setAlignment(Qt::AlignCenter);
  title->setFont(QFont("Noto Sans CJK SC", 54, QFont::Bold));
  layout->addWidget(title);

  const QString active_version = readActiveVersion();
  auto *active = new QLabel(active_version == "legacy"
                              ? QStringLiteral("上次使用：原系统版")
                              : QStringLiteral("上次使用：当前稳定版"));
  active->setAlignment(Qt::AlignCenter);
  active->setFont(QFont("Noto Sans CJK SC", 27));
  active->setStyleSheet("color: #aab4bd;");
  layout->addWidget(active);

  auto *buttons = new QHBoxLayout();
  buttons->setSpacing(40);

  auto *stable = new QPushButton(QStringLiteral("当前稳定版\nopenpilot 0.9.7"));
  auto *legacy = new QPushButton(QStringLiteral("原系统版\nopenpilot 0.9.6"));
  for (QPushButton *button : {stable, legacy}) {
    button->setMinimumHeight(360);
    button->setFont(QFont("Noto Sans CJK SC", 36, QFont::DemiBold));
  }
  stable->setStyleSheet(
    "QPushButton { background: #16875d; border: 3px solid #49c795; border-radius: 8px; }"
    "QPushButton:pressed { background: #0f6846; }");
  legacy->setStyleSheet(
    "QPushButton { background: #303941; border: 3px solid #6d7882; border-radius: 8px; }"
    "QPushButton:pressed { background: #222a30; }");
  buttons->addWidget(stable);
  buttons->addWidget(legacy);
  layout->addLayout(buttons);

  auto *countdown = new QLabel();
  countdown->setAlignment(Qt::AlignCenter);
  countdown->setFont(QFont("Noto Sans CJK SC", 27));
  countdown->setStyleSheet("color: #c7d0d8;");
  layout->addWidget(countdown);

  QObject::connect(stable, &QPushButton::clicked, [&app]() { app.exit(kStableExitCode); });
  QObject::connect(legacy, &QPushButton::clicked, [&app]() { app.exit(kLegacyExitCode); });

  int seconds_left = kTimeoutSeconds;
  auto update_countdown = [&]() {
    countdown->setText(QStringLiteral("%1 秒后自动进入当前稳定版").arg(seconds_left));
  };
  update_countdown();

  QTimer timer;
  QObject::connect(&timer, &QTimer::timeout, [&]() {
    if (--seconds_left <= 0) {
      app.exit(kStableExitCode);
    } else {
      update_countdown();
    }
  });
  timer.start(1000);

  window.showFullScreen();
  return app.exec();
}
