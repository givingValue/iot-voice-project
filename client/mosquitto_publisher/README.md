# Mosquitto Publisher

## Table of Contents
- [Mosquitto Publisher](#mosquitto-publisher)
  - [Table of Contents](#table-of-contents)
    - [Console Mosquitto Publisher](#console-mosquitto-publisher)
      - [Install the Mosquitto dependencies in a Debian based distribution](#install-the-mosquitto-dependencies-in-a-debian-based-distribution)
      - [Config and run the Console Mosquitto Publisher](#config-and-run-the-console-mosquitto-publisher)
    - [Daemon Mosquitto Publisher](#daemon-mosquitto-publisher)
      - [Install the dependencies in a Debian based distribution](#install-the-dependencies-in-a-debian-based-distribution)
      - [Config and run the Daemon Mosquitto Publisher](#config-and-run-the-daemon-mosquitto-publisher)
      - [Considerations](#considerations)
    - [References](#references)

### Console Mosquitto Publisher

#### Install the Mosquitto dependencies in a Debian based distribution
To install the mosquitto dependencies in Debian based distribution you have to execute the next commands:

* Add the mosquitto repository:
  ```bash
  $ sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
  $ sudo apt-get update
  ```

* Install mosquitto and its dependencies:
  ```bash
  $ sudo apt install -y mosquitto mosquitto-clients mosquitto-dev
  ```

#### Config and run the Console Mosquitto Publisher
To set up the console mosquitto publisher you have to execute the next commands:

* Compile the mosquitto_publisher:
  ```bash
  $ cd ./console_mosquitto_publisher

  $ gcc -g mosquitto_password_publisher.c -o mosquitto_password_publisher -lmosquitto
  or
  $ gcc -g mosquitto_ssl_publisher.c -o mosquitto_ssl_publisher -lmosquitto
  ```
  > The compilation of the mosquitto publisher with password or ssl as authentication method will depend on your security needs.

* Execute the mosquitto publisher:

  Example:
  ```bash
  $ ./mosquitto_password_publisher --broker 3.238.84.216 --port 3000 --topic /iot/channel/1 --username iot_user --password 4741iot --data-file ./data.txt
  or
  $ ./mosquitto_password_publisher --broker 3.238.84.216 --port 3000 --topic /iot/channel/1 --ca-file ./root.ca  --cert-file ./cert.crt --key-file ./cert.key --data-file ./data.txt
  ```

### Daemon Mosquitto Publisher

#### Install the dependencies in a Debian based distribution
To install the needed dependencies in a Debian based distribution you have to execute the next commands:

* Add the mosquitto repository:
  ```bash
  $ sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
  $ sudo apt-get update
  ```

* Install mosquitto and other dependencies:
  ```bash
  $ sudo apt install -y mosquitto mosquitto-clients mosquitto-dev libsystemd-dev
  ```

#### Config and run the Daemon Mosquitto Publisher
To set up the daemon mosquitto publisher you have to execute the next commands:

* Compile the mosquitto_publisher:
  ```bash
  $ cd ./daemon_mosquitto_publisher

  $ gcc -g mosquitto_publisher.c -o mosquitto_publisher -lsystemd -lmosquitto
  ```

* Move all the files to their respective places:
  ```bash
  $ sudo mkdir /etc/mosquitto-publisher

  $ sudo mv ./mosquitto_publisher /usr/local/bin/mosquitto_publisher

  $ sudo mv ./mosquitto-publisher.service /usr/lib/systemd/system

  $ sudo mv ./mosquitto-publisher.socket /usr/lib/systemd/system

  $ sudo mv ./mosquitto-publisher.conf /etc/mosquitto-publisher
  ```
  > Remember to make the adjustments according to your needs in the files.


* Validate that the ``mosquitto-publisher.service`` is recognised by systemd:
  ```bash
  $ sudo systemctl daemon-reload

  $ sudo systemctl list-unit-files mosquitto-publisher.service
  UNIT FILE                   STATE    PRESET 
  mosquitto-publisher.service disabled enabled

  1 unit files listed.
  ```

* Start the service and review the statuses:
  ```bash
  $ sudo systemctl start mosquitto-publisher.service

  $ sudo systemctl status mosquitto-publisher.service

  $ sudo systemctl status mosquitto-publisher.socket
  ```

* Check the logs to validate that everything is ok:
  ```bash
  $ sudo journalctl -u mosquitto-publisher.service | tail -n 20
  or
  $ sudo cat /var/log/mosquitto-publisher/mosquitto-publisher.log | tail -n 20
  ```
#### Considerations

* Command line arguments override file arguments.
* ``Autotools`` is going to be add in the future in order to ease the configuration process.
* Since the daemon of the mosquitto publisher allows the ``reload`` of the process, you can change the ``config`` file, reload the service and all the changes are going to be applied:
  ```bash
  $ sudo systemctl reload mosquitto-publisher.service
  ```
* In the reload procedure, **only** the changes in the ``config`` file are going to be taken into account. Command line arguments are not going to be read.
* The daemon of the mosquitto publisher only use user-password as authentication method in this moment.

### References
* [Daemon Example in C](https://lloydrochester.com/post/c/unix-daemon-example/)
* [Systemd and Autotools](https://lloydrochester.com/post/autotools/systemd-service-daemon-autotools/)
* [Status, Reloading and Journalling in Systemd](https://lloydrochester.com/post/unix/systemd_journal/)
* [Systemd: A Service and a Socket](https://lloydrochester.com/post/unix/systemd_sockets/)
* [Journald vs Syslog](https://openobserve.ai/blog/journald-vs-syslog/)
* [Unable to find package libsystemd](https://stackoverflow.com/questions/73890414/unable-to-find-package-libsystemd)

