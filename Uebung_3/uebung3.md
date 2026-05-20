# Security Engineering Übung 3

## Aufgabe 1

Verhindern, dass Systemzeit verändert wird:

```bash
    ntpdate -q <server>
```

-q Query only – don't set the clock.

Debug-Ausgaben aktivieren:

```bash
    ntpdate -d <server>
```

-d Enable the debugging mode, in which ntpdate will go through all the steps, but
not adjust the local clock and using an unprivileged port. Information useful
for general debugging will also be printed.

### Offiziell erreichbare NTP-Server der physikalisch-technischen Bundesanstalt:

    PTB Zeitserver 1: ptbtime1.ptb.de
    PTB Zeitserver 2: ptbtime2.ptb.de
    PTB Zeitserver 3: ptbtime3.ptb.de

### Offiziell erreichbare NTP Server des HIZ:

    ntp1.hiz-saarland.de
    ntp2.hiz-saarland.de
    ntp3.hiz-saarland.de
    ntp4.hiz-saarland.de

### Weitere offiziell erreichbare NTP-Server:

    0.de.pool.ntp.org
    1.de.pool.ntp.org
    2.de.pool.ntp.org
    3.de.pool.ntp.org
    ntp.web.de
    ntp1.t-online.de
    time.google.com
    time1.google.com
    time2.google.com
    time3.google.com

## Aufgabe 2

```bash
fgrep 'ranking-number' fussball-tabelle.html | \
sed -E 's/.*ranking-number">([0-9]+).*mr10"><\/span> ([^<]+)<.*/\1. \2/' \
>tabelle.txt
```
