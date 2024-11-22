# Mosquitto Client

## Table of Contents
- [Mosquitto Client](#mosquitto-client)
  - [Table of Contents](#table-of-contents)
    - [Install the Client in Ubuntu](#install-the-client-in-ubuntu)
    - [Config the Client with Password](#config-the-client-with-password)
    - [References](#references)

### Install the Client in Ubuntu
To install the mosquitto client in Ubuntu you have to execute the next commands:

* Add the mosquitto repository:
```
$ sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
$ sudo apt-get update
```

* Install mosquitto and its dependencies:
```
$ sudo apt install -y mosquitto mosquitto-clients mosquitto-dev
```

### Config the Client with Password
To set up the mosquitto client with password you have to execute the next commands:

* Compile the client:
```
$ gcc -o mosquitto_password_client.exe mosquitto_password_client.c -lmosquitto
or
$ gcc -o mosquitto_ssl_client.exe mosquitto_ssl_client.c -lmosquitto
```
> ℹ️: The compilation of the client with password or ssl will depend on your security needs.

* Execute the client:

Example:
```
$ ./mosquitto_password_client.exe --broker 3.238.84.216 --port 3000 --topic /iot/channel/1 --username iot_user --password 4741iot --data-file ./data.txt
or
$ ./mosquitto_password_client.exe --broker 3.238.84.216 --port 3000 --topic /iot/channel/1 --ca-file ./ca.pem  --cert-file ./cert.pem --key-file ./cert.key --data-file ./data.txt
```

### References