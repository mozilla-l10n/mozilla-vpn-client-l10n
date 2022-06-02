### DUMMY PRO FILE
HEADERS += l18nstrings.h
SOURCES += l18nstrings_p.cpp
SOURCES += ../l18nstrings.cpp
TRANSLATIONS += translations.ts
HEADERS += $$files(../../src/*.h, true)
SOURCES += $$files(../../src/*.cpp, true)
RESOURCES += $$files(../../src/*.qrc, true)
HEADERS += $$files(../../nebula/*.h, true)
SOURCES += $$files(../../nebula/*.cpp, true)
RESOURCES += $$files(../../nebula/*.qrc, true)
