# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.9.1
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x05\xe9\
<\
?xml version=\x221.\
0\x22?>\x0a<algorithm \
year=\x222015\x22 auth\
or=\x22Christoph Wi\
ck\x22>\x0a    <name>\x0a\
        <string>\
Example algorith\
m</string>\x0a     \
   <string lang=\
\x22de\x22>Beispielalg\
orithmus</string\
>\x0a    </name>\x0a  \
  <description>\x0a\
        <string>\
This is just an \
example algorith\
m that will set \
the tuning curve\
 to equal tempra\
ment.</string>\x0a \
       <string l\
ang=\x22de\x22>Dies is\
t nur ein Beispi\
elalgorithmus, d\
er die Stimmkurv\
e auf eine gleic\
htemperierte Sti\
mmung bringt.</s\
tring>\x0a    </des\
cription>\x0a    <p\
aram id=\x22concert\
Pitch\x22 type=\x22dou\
ble\x22 min=\x22430\x22 m\
ax=\x22450\x22 default\
=\x22440\x22 precision\
=\x221\x22>\x0a        <l\
abel>\x0a          \
  <string>Concer\
t pitch</string>\
\x0a            <st\
ring lang=\x22de\x22>K\
ammerton</string\
>\x0a        </labe\
l>\x0a        <desc\
ription>\x0a       \
     <string>The\
 desired concert\
 pitch.</string>\
\x0a            <st\
ring lang=\x22de\x22>D\
er gew\xc3\xbcnschte K\
ammerton.</strin\
g>\x0a        </des\
cription>\x0a    </\
param>\x0a    <para\
m id=\x22dummyList\x22\
 type=\x22list\x22 def\
ault=\x22entry_2\x22>\x0a\
        <label>\x0a\
            <str\
ing>Dummy list</\
string>\x0a        \
    <string lang\
=\x22de\x22>Dummy-List\
e</string>\x0a     \
   </label>\x0a    \
    <description\
>\x0a            <s\
tring>Select any\
 entry.</string>\
\x0a            <st\
ring lang=\x22de\x22>W\
\xc3\xa4hle einen beli\
ebigen Eintrag.<\
/string>\x0a       \
 </description>\x0a\
        <entry v\
alue=\x22entry_1\x22>\x0a\
            <str\
ing>Entry 1</str\
ing>\x0a           \
 <string lang=\x22d\
e\x22>Eintrag 1</st\
ring>\x0a        </\
entry>\x0a        <\
entry value=\x22ent\
ry_2\x22>\x0a         \
   <string>Entry\
 2</string>\x0a    \
        <string \
lang=\x22de\x22>Eintra\
g 2</string>\x0a   \
     </entry>\x0a  \
  </param>\x0a</alg\
orithm>\x0a\
"

qt_resource_name = b"\
\x00\x0a\
\x06\x9d\xaa\x83\
\x00a\
\x00l\x00g\x00o\x00r\x00i\x00t\x00h\x00m\x00s\
\x00\x14\
\x00\xa5q\x9c\
\x00e\
\x00x\x00a\x00m\x00p\x00l\x00e\x00a\x00l\x00g\x00o\x00r\x00i\x00t\x00h\x00m\x00.\
\x00x\x00m\x00l\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x1a\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01^\x09r?\xe0\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
