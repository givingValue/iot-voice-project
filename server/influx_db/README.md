# InfluxDB

## Table of Contents
- [InfluxDB](#influxdb)
  - [Table of Contents](#table-of-contents)
    - [Deploy InfluxDB in a Server](#deploy-influxDB-in-a-server)
    - [Schema of the Measure](#schema-of-the-measure)
    - [Additional Configurations](#additional-configurations)
    - [References](#references)

### Deploy InfluxDB in a Server
For deploying InfluxDB in a Server you have to execute the next commands:

* Copy the ``docker compose`` file into a path that best fits to you:
    ```
    cp ./docker-compose.yml <path>
    ```

* Change the properties inside the ``docker compose`` file to meet your needs:
    ```
    nano ./docker-compose.yml

    ...
    5  - 8086:8086
    ...
    11  DOCKER_INFLUXDB_INIT_ORG: <org_name>
    12  DOCKER_INFLUXDB_INIT_BUCKET: <bucket_name>
    ...
    ```

* Create the ``.env`` files for each secret property:
    ```
    nano .env.influxdb2-admin-username

    <admin-usermane>

    nano .env.influxdb2-admin-password

    <admin-password>

    nano .env.influxdb2-admin-token

    <admin-token>
    ```
    > ℹ️: The .env files need to be in the same folder of the docker compose file.

* Execute the ``docker compose`` file:
    ```
    sudo docker compose up -d
    ```

### Schema of the Measure
Current schema of the measure ``voice_sensor``:
* measure name: voice_sensor.
* tag 1: sensor_id.
* tag 2: room.
* field 1: voice_gender.

### Additional Configurations
There are some additional configurations such as:
* Change the retention period of the bucket to 30 days.

### References
* [Install InfluxDB OSS v2](https://docs.influxdata.com/influxdb/v2/install/)
* [Get started with InfluxDB](https://docs.influxdata.com/influxdb/v2/get-started/)
* [Set up InfluxDB](https://docs.influxdata.com/influxdb/v2/get-started/setup/)
* [Get started writing data](https://docs.influxdata.com/influxdb/v2/get-started/write/)
* [Get started querying data](https://docs.influxdata.com/influxdb/v2/get-started/query/)
* [Get started processing data](https://docs.influxdata.com/influxdb/v2/get-started/process/)
* [Get started visualizing data](https://docs.influxdata.com/influxdb/v2/get-started/visualize/)
* [InfluxDB schema design](https://docs.influxdata.com/influxdb/v2/write-data/best-practices/schema-design/)
* [Apache Superset](https://www.influxdata.com/integration/apache-superset/)
* [An Introduction to Apache Superset: An Open Source BI solution](https://www.influxdata.com/blog/introduction-apache-superset/)