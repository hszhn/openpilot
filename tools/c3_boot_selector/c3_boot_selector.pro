QT += widgets gui-private
CONFIG += c++17 release
CONFIG -= app_bundle
TARGET = c3-version-selector
SOURCES += main.cpp
LIBS += -lwayland-client
