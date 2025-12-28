# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.9.1
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x0f2\
<\
?xml version=\x221.\
0\x22?>\x0a<algorithm \
year=\x222012-2015\x22\
 author=\x22Haye Hi\
nrichsen\x22>\x0a    <\
name>\x0a        <s\
tring>Entropy mi\
nimizer</string>\
\x0a        <string\
 lang=\x22de\x22>Entro\
pieminimierer</s\
tring>\x0a        <\
string lang=\x22zh\x22\
>\xe7\x86\xb5\xe6\x9e\x81\xe5\xb0\x8f</stri\
ng>\x0a    </name>\x0a\
    <description\
>\x0a        <strin\
g>This algorithm\
 minimizes the e\
ntropy of the su\
perposed spectra\
 of all keys (se\
e user manual).<\
/string>\x0a       \
 <string lang=\x22d\
e\x22>Dieser Algori\
thmus minimiert \
die Entropie des\
 \xc3\xbcberlagerten S\
pektrums aller T\
asten (siehe Bed\
ienungsanleitung\
).</string>\x0a    \
    <string lang\
=\x22zh\x22>\xe7\xae\x97\xe6\xb3\x95\xe6\x98\xaf\xe6\
\x89\x80\xe6\x9c\x89\xe9\x94\xae\xe5\x8f\xa0\xe5\x8a\xa0\xe9\xa2\
\x91\xe8\xb0\xb1\xe7\x86\xb5\xe7\x9a\x84\xe6\x9c\x80\xe5\xb0\x8f\
\xe5\x8c\x96\xef\xbc\x88\xe5\x8f\x82\xe8\xa7\x81\xe7\x94\xa8\xe6\
\x88\xb7\xe6\x89\x8b\xe5\x86\x8c\xef\xbc\x89.</st\
ring>\x0a    </desc\
ription>\x0a    <pa\
ram id=\x22accuracy\
\x22 type=\x22list\x22 de\
fault=\x22standard\x22\
>\x0a        <label\
>\x0a            <s\
tring>Calculatio\
n accuracy</stri\
ng>\x0a            \
<string lang=\x22de\
\x22>Berechnungsgen\
auigkeit</string\
>\x0a            <s\
tring lang=\x22zh\x22>\
\xe8\xae\xa1\xe7\xae\x97\xe7\xb2\xbe\xe5\xba\xa6</st\
ring>\x0a        </\
label>\x0a        <\
description>\x0a   \
         <string\
>Select the accu\
racy of the algo\
rithm. A higher \
accuracy will ta\
ke more computin\
g time.</string>\
\x0a            <st\
ring lang=\x22de\x22>W\
\xc3\xa4hlen Sie die G\
enauigkeit des A\
lgorithmus. Eine\
 gr\xc3\xb6\xc3\x9fere Genau\
igkeit wird eine\
 l\xc3\xa4ngere Berech\
nungszeit in Ans\
pruch nehmen.</s\
tring>\x0a         \
   <string lang=\
\x22zh\x22>\xe9\x80\x89\xe6\x8b\xa9\xe7\xae\x97\xe6\xb3\
\x95\xe7\xb2\xbe\xe5\xba\xa6\xef\xbc\x8c\xe8\xbe\x83\xe9\xab\x98\
\xe7\x9a\x84\xe7\xb2\xbe\xe5\xba\xa6\xe5\xb0\x86\xe8\x8a\xb1\xe8\
\xb4\xb9\xe8\xae\xa1\xe7\xae\x97\xe6\x97\xb6\xe9\x97\xb4\xe3\x80\
\x82</string>\x0a     \
   </description\
>\x0a        <entry\
 value=\x22low\x22>\x0a  \
          <strin\
g>Low</string>\x0a \
           <stri\
ng lang=\x22de\x22>Nie\
drig</string>\x0a  \
          <strin\
g lang=\x22zh\x22>\xe4\xbd\x8e<\
/string>\x0a       \
 </entry>\x0a      \
  <entry value=\x22\
standard\x22>\x0a     \
       <string>S\
tandard</string>\
\x0a            <st\
ring lang=\x22de\x22>S\
tandard</string>\
\x0a            <st\
ring lang=\x22zh\x22>\xe6\
\xa0\x87\xe5\x87\x86</string>\x0a \
       </entry>\x0a\
        <entry v\
alue=\x22high\x22>\x0a   \
         <string\
>High</string>\x0a \
           <stri\
ng lang=\x22de\x22>Hoc\
h</string>\x0a     \
       <string l\
ang=\x22zh\x22>\xe9\xab\x98</st\
ring>\x0a        </\
entry>\x0a        <\
entry value=\x22inf\
inite\x22>\x0a        \
    <string>Infi\
nite</string>\x0a  \
          <strin\
g lang=\x22de\x22>Unen\
dlich</string>\x0a \
           <stri\
ng lang=\x22zh\x22>\xe6\x97\xa0\
\xe9\x99\x90</string>\x0a   \
     </entry>\x0a  \
  </param>\x0a    <\
param id=\x22seed\x22 \
type=\x22int\x22 defau\
lt=\x220\x22 min=\x220\x22 m\
ax=\x22999999\x22 slid\
er=\x22false\x22>\x0a    \
    <label>\x0a    \
        <string>\
Seed</string>\x0a  \
          <strin\
g lang=\x22de\x22>Seed\
</string>\x0a      \
      <string la\
ng=\x22zh\x22>\xe7\xa7\x8d\xe5\xad\x90</\
string>\x0a        \
</label>\x0a       \
 <description>\x0a \
           <stri\
ng>Set this valu\
e to any integer\
 number to initi\
alize the pseudo\
 random number g\
enerator to comp\
ute a determinis\
tic tuning. Set \
the seed to 0 to\
 initialize the \
generator with a\
 random number g\
enerated by the \
system.</string>\
\x0a            <st\
ring lang=\x22de\x22>S\
etzen Sie diesen\
 Wert auf eine b\
eliebige ganze Z\
ahl, um den Pseu\
dozufallszahleng\
enerator zu init\
ializieren, womi\
t eine determini\
stische Stimmung\
 berechnet wird.\
 Setzen Sie den \
Seed auf 0, um d\
en Generator mit\
 einer Zufallsza\
hl zu initializi\
eren, die vom Sy\
stem generiert w\
ird.</string>\x0a  \
          <strin\
g lang=\x22zh\x22>\xe8\xae\xbe\xe7\
\xbd\xae\xe8\xbf\x99\xe4\xb8\xaa\xe5\x80\xbc\xe4\xb8\xba\xe4\xbb\
\xbb\xe4\xbd\x95\xe6\x95\xb4\xe6\x95\xb0\xef\xbc\x8c\xe7\x94\xa8\
\xe4\xba\x8e\xe5\x88\x9d\xe5\xa7\x8b\xe5\x8c\x96\xe4\xbc\xaa\xe9\
\x9a\x8f\xe6\x9c\xba\xe6\x95\xb0\xe5\x8f\x91\xe7\x94\x9f\xe5\x99\
\xa8\xef\xbc\x8c\xe6\x9d\xa5\xe8\xae\xa1\xe7\xae\x97\xe7\xa1\xae\
\xe5\xae\x9a\xe8\xb0\x83\xe5\xbe\x8b\xe3\x80\x82\xe7\xa7\x8d\xe5\
\xad\x90\xe4\xb8\xba0\xe6\x97\xb6\xe5\x88\x9d\xe5\xa7\x8b\xe5\
\x8c\x96\xe7\x94\xb1\xe7\xb3\xbb\xe7\xbb\x9f\xe4\xba\xa7\xe7\x94\
\x9f\xe9\x9a\x8f\xe6\x9c\xba\xe6\x95\xb0\xe3\x80\x82</s\
tring>\x0a        <\
/description>\x0a  \
  </param>\x0a    <\
param id=\x22entrop\
y\x22 type=\x22double\x22\
 default=\x220\x22 sli\
der=\x22false\x22 spin\
Box=\x22false\x22 line\
Edit=\x22true\x22 prec\
ision=\x226\x22 readOn\
ly=\x22true\x22 update\
Interval=\x22500\x22>\x0a\
        <label>\x0a\
            <str\
ing>Entropy</str\
ing>\x0a           \
 <string lang=\x22d\
e\x22>Entropie</str\
ing>\x0a           \
 <string lang=\x22z\
h\x22>\xe7\x86\xb5</string>\x0a\
        </label>\
\x0a        <descri\
ption>\x0a         \
   <string>This \
value displays t\
he current compu\
ted value of the\
 entropy. A valu\
e of 0 states th\
at there was no \
calculation yet.\
</string>\x0a      \
      <string la\
ng=\x22de\x22>Dieser W\
ert zeigt den ak\
tuell berechnete\
n Wert der Entro\
pie an. Ein Wert\
 von 0 besagt, d\
ass noch keine B\
erechnung durchg\
ef\xc3\xbchrt wurde.</\
string>\x0a        \
    <string lang\
=\x22zh\x22>\xe8\xaf\xa5\xe5\x80\xbc\xe6\x98\xbe\xe7\
\xa4\xba\xe7\x86\xb5\xe7\x9a\x84\xe5\xbd\x93\xe5\x89\x8d\xe8\xae\
\xa1\xe7\xae\x97\xe5\x80\xbc\xe3\x80\x82\xe5\x80\xbc\xe4\xb8\xba\
0\xe8\xa1\xa8\xe7\xa4\xba\xe6\xb2\xa1\xe6\x9c\x89\xe8\xae\xa1\
\xe7\xae\x97\xe3\x80\x82</string>\x0a\
        </descri\
ption>\x0a    </par\
am>\x0a</algorithm>\
\x0a\
"

qt_resource_name = b"\
\x00\x0a\
\x06\x9d\xaa\x83\
\x00a\
\x00l\x00g\x00o\x00r\x00i\x00t\x00h\x00m\x00s\
\x00\x14\
\x01\xa9\xed<\
\x00e\
\x00n\x00t\x00r\x00o\x00p\x00y\x00m\x00i\x00n\x00i\x00m\x00i\x00z\x00e\x00r\x00.\
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
