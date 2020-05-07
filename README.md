*Please :star: this repo if you find it useful*

<p align="left"><br>
<a href="https://paypal.me/eyalco1967?locale.x=he_IL" target="_blank"><img src="http://khrolenok.ru/support_paypal.png" alt="PayPal" width="250" height="48"></a>
</p>

# Read Your Meter

The read your meter integration can be used to read your house water consumption.

![Heat Map](./docs/water_meter.jpg)

There is currently support for the following device types within Home Assistant:

- [Sensor](#sensor)

## Requirements

For the integration to work, you need the following:

- Account in read your meter
- Selenuim standalone chrome running on same device as Home Assisatnt.

## Install Selenuim

For installing [Sellenuim](https://www.selenium.dev/) please refere to the [offical documentation](https://www.selenium.dev/documentation/en/selenium_installation).

If you want to run the Sellenuim on Raspbery Pi, you can use the following command to download and start container with the following command:

```
docker run -d -p 4444:4444 --name selenium chadbutz/rpi-selenium-standalone-chrome
```

or with docker-compose

```
TBD
```