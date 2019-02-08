# Cél

Szimulálni egy fogyasztókkal teli hálózaton a be/ki kapcsolásokat,
és a mért értékeket

A szimulált értékeket log fileba írni.

## Eredmény formátum

Eseményekből képzett lista
Esemény:

  - Be / kikapcsolási esemény, timestampje van, meg fogyasztója
  - Mért érték, timestamp, meg fogyasztás elmúlt timestamp óta

## Szimulálandók

### WC lámpa
Nap közben véletlen időpontokban felkapcsolódik többször is.
Két perc után lekapcsol. Keveset fogyaszt.

### Íróasztal lámpa

Reggel bekapcsolódik, és sokáig égve marad.

### Olajradiátor

Mondjuk két órán keresztül be van kapcsolva.
Akkor kb két percenént bekapcsol, sokat fogyaszt.
Utána 3 percre kikapcsol.

### Mikró

Dél körül sokszor van bekapcsolva 3 percre.
Olyankor sokat fogyaszt, hektikus terheléssel.

### Hűtó

Óránként bekapcsol 5 percre, egész nap 2 kW eszik.

### FanCoil

Munkaidőben bekapcsolódik, é akkor sokat fogyaszt,
közepes állapotban keveset. és ki is lehet kapcsolva.

### Szerverek

Egész nap be vannak kapcsolva, kb konstans fogyasztással.
Ez valamennyit szór.

## Fogyasztó

Eddigiek alapján van **neve**.
**Teljesítménye**, és annak **szórása**.

Üzemideje. Az egy időtartam, ami alatt a berendezés működik.
**Kezdete** és **vége** van.

Üzemidő alatt lehet ciklikus, amikor ki / be
kapcsolódik véletlenszerűen.

Ebből kb az üzemidő egy lista, amelyik be / ki párosokat tartalmaz.
Időtartamok nem átfedők.

Mondjuk a fogyasztó inicializáláskor feltölti az üzemidő listáját.

Meg lehet tőle kérdezni, egy időszakra, hogy mennyit fogyaszt.
Ilyenkor veszi az időszak alatti bekapcsoltságait  a listából, és
srosol rá fogyasztást.

Meg lehet kérdezni, milyen események voltak az időszakban.
Odaadja be / ki + timestamp formában.

## Hálózat

Egy lista a fogyasztó példányokból.



## Mérő

Megkapja a hálózat egy részhalmazát

Almérő csak részhamazt kap.

Főmérő meg teljes hálózatot.

## Mérés

Egyszerűség kedvéért atom pontos, és fix 5 perces / negyedórás, vmi,
csak legyen 60 osztója. Sőt inkább hány mérés / nap.
15 perc = 96 mérés. 5 perc = 288 mérés.

Van egy listája a teljes hálózatról. abból minden fogyasztóra
megkérdezi, mennyi volt a fogyasztása az aktuális 5 perces időszakban.

Ezt odaadja a mérőnek. Az meg tudja mondani, mennyi a hozzá tartozó
részhalmazon a szumma fogyasztás.

Nem mellesleg megkérdezi, hogy milyen események voltak az időszak alatt.
Ezeket sorba rakja. Végére oda biggyeszti a mérők eredményeit is.