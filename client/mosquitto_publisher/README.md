# Mosquitto Publisher

## Table of Contents
- [Mosquitto Publisher](#mosquitto-publisher)
  - [Table of Contents](#table-of-contents)
    - [Install the Mosquitto dependencies in Ubuntu](#install-the-mosquitto-dependencies-in-ubuntu)
    - [Config the Publisher Client](#config-the-publisher-client)
    - [References](#references)

### Install the Mosquitto dependencies in Ubuntu
To install the mosquitto dependencies in Ubuntu you have to execute the next commands:

* Add the mosquitto repository:
```
$ sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
$ sudo apt-get update
```

* Install mosquitto and its dependencies:
```
$ sudo apt install -y mosquitto mosquitto-clients mosquitto-dev
```

### Config the Publisher Client
To set up the mosquitto publisher client you have to execute the next commands:

* Compile the publisher client:
```
$ gcc -o mosquitto_password_publisher.exe mosquitto_password_publisher.c -lmosquitto
or
$ gcc -o mosquitto_ssl_publisher.exe mosquitto_ssl_publisher.c -lmosquitto
```
> ℹ️: The compilation of the client with password or ssl will depend on your security needs.

* Execute the publisher client:

Example:
```
$ ./mosquitto_password_publisher.exe --broker 3.238.84.216 --port 3000 --topic /iot/channel/1 --username iot_user --password 4741iot --data-file ./data.txt
or
$ ./mosquitto_password_publisher.exe --broker 3.238.84.216 --port 3000 --topic /iot/channel/1 --ca-file ./root.ca  --cert-file ./cert.crt --key-file ./cert.key --data-file ./data.txt
```

### References