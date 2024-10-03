# Monitor Aktivierung
Aktiviert den Monitor, wenn dieser sich im Standby Modus befinden sollte.

Zur Realisierung der Aktivierungsfunktion wird ein Bewegungsmelder (Aquara) mittels [Zigbee2Mqtt](https://www.zigbee2mqtt.io/) eingesetzt. 
Bei Erkennung einer Bewegung sendet der Motion Sensor ein Zigbee Signal an Zigbee2Mqtt, welches wiederum einen Eintrag im entsprechenden Topic schreibt.
Dieses Topic wird von diesem Programm überwacht und die Aktivierung des Monitors gestartet.

Als Motion Sensor wird ein Aquara [FP1E](https://www.aqara.com/de/product/presence-sensor-fp1e-specs/) eingesetzt. 
Es ist jedoch auch jeder x-beliebige PIR Sensor möglich. Es muss schlussendlich nur eine MQTT Message geschrieben werden.

## Requirements
Installiere `cec-utils`:
```commandline
sudo apt install cec-utils
```

Damit die Hotkeys funktionieren muss der Benutzer, der das Skript ausführt, zu der Gruppe `tty` gehören:
```commandline
sudo usermod -a -G tty,input $USER
```
Dies muss zwingend vor [Notwendige Python Module](#notwendige-python-module) ausgeführt werden.

### Notwendige Python Module
Zusätzlich müssen die abhängigen Python Module installiert werden:
```commandline
pip install -r requirements.txt
```


## Programm in den Autostart legen
```commandline
python3 main.py
```
With raspberry pi's LXDE change following file:
`~/.config/lxsession/LXDE-pi/autostart`
with
```
# Motion detection to activate monitor
@python /home/pi/ScreenActivationOnMotion/main.py
```
