#include <stdio.h>
#include <mosquitto.h>

const int SUCCESS_CODE = 0;
const int ERROR_CODE = -1;

int main(){
    const int MOSQUITTO_SUCCESS_STATUS = 0;
    const char *BROKER_HOST = "";
    const int BROKER_PORT = 1883;

    int status;
    struct mosquitto *mosquitto_client;

    mosquitto_lib_init();

    mosquitto_client = mosquitto_new("publisher_test", true, NULL);

    status = mosquitto_connect(mosquitto_client, BROKER_HOST, BROKER_PORT, 60);

    if (status != MOSQUITTO_SUCCESS_STATUS) {
        printf("Client could not connect to the broker in: %s:%d\n", BROKER_HOST, BROKER_PORT);
        printf("Error code: %d\n", status);
        mosquitto_destroy(mosquitto_client);
        return ERROR_CODE;
    } 
    
    printf("Client connected to the broker in: %s:%d\n", BROKER_HOST, BROKER_PORT);

    mosquitto_publish(mosquitto_client,NULL, "test/t1", 6, "hello", 0, false);

    mosquitto_disconnect(mosquitto_client);
    mosquitto_destroy(mosquitto_client);

    mosquitto_lib_cleanup();

    return SUCCESS_CODE;
}