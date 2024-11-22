# Mosquitto Broker

## Table of Contents
- [Mosquitto Broker](#mosquitto-broker)
  - [Table of Contents](#table-of-contents)
    - [Install the Broker in Ubuntu Server](#install-the-broker-in-ubuntu-server)
    - [Config the Broker with Passwords](#config-the-broker-with-passwords)
    - [References](#references)

### Install the Broker in Ubuntu Server
To install the mosquitto broker in Ubuntu Server you have to execute the next commands:

* Add the mosquitto repository:
```
$ sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
$ sudo apt-get update
```

* Install mosquitto and its dependencies:
```
$ sudo apt install -y mosquitto mosquitto-clients
```

### Config the Broker with Passwords
To set up the mosquitto broker with passwords in Ubuntu Server you have to execute the next commands:

* Create the password file:
```
$ sudo mosquitto_passwd -c passwordfile <username>
$ sudo chown mosquitto:mosquitto passwordfile
```
> ℹ️: It is recommended to run this command at ``/etc/mosquitto/``.
> ℹ️: The password of the username will be requested just after executing the command.

* Create the config file:
```
$ cd /etc/mosquitto/conf.d
$ sudo touch iot_broker.conf
```

* Put the config options into the config file:

Example:
```
per_listener_settings true
log_dest file /var/log/mosquitto/mosquitto.log
log_timestamp_format %Y-%m-%d_%H:%M:%S

listener 3000 192.168.224.30
allow_anonymous false
password_file /etc/mosquitto/passwordfile
max_inflight_messages 0
```
> ℹ️: Use the file ``mosquitto_password.conf.template`` as guide.

* Run the mosquitto command:
```
$ sudo mosquitto -c /etc/mosquitto/conf.d/iot_broker.conf -d
```
> ℹ️: To verify that the broker is up and running you can check the logs by executing: ``sudo cat /var/log/mosquitto/mosquitto.log``.

### References