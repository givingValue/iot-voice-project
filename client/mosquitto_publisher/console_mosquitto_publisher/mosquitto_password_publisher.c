#include <stdio.h>
#include <mosquitto.h>
#include <unistd.h>
#include <stdlib.h> 
#include <string.h>
#include <sys/stat.h>
#include <signal.h>

const int SUCCESS_CODE = 0;
const int ERROR_CODE = -1;

struct mosquitto *mosquitto_client;

char *get_argument(int arguments_length, char **arguments, char *argument, bool required, char *default_value) {
    char *argument_value;

    if (arguments_length == 1) {
        printf("There are not arguments.\n");
        exit(-1);
    }

    for(int index = 1; index < arguments_length; index++) {
        argument_value = arguments[index];

        if (strcmp(argument_value, argument) == 0) {
            argument_value = arguments[index + 1];
            break;
        }

        if ((index == arguments_length - 1) && (default_value)) {
            argument_value = default_value;
            break;
        }

        if ((index == arguments_length - 1) && (required)) {
            printf("The argument %s must be provided.\n", argument);
            exit(-1);
        }
    }

    return argument_value;
}

char *read_data_file(const char *file_path, int max_message_bytes) {
    FILE *file;
    struct stat file_stats;
    char *message = malloc(sizeof(char) * max_message_bytes);

    stat(file_path, &file_stats);

    if(file_stats.st_size <= 1) {
        return NULL;
    }

    file = fopen(file_path, "r");
    fgets(message, max_message_bytes, file);
    file = freopen(file_path, "w", file);
    fclose(file);

    return message;
}

void signal_interrupt(){
    printf("\nClient interrupted.\n");

    mosquitto_disconnect(mosquitto_client);
    mosquitto_destroy(mosquitto_client);
    mosquitto_lib_cleanup();

    exit(SUCCESS_CODE);
}

int main(int argc, char **argv){
    const bool CLEAN_SESSION = true;
    const int KEEPALIVE = 60;
    const int TIMEOUT = 1000;
    const int MAX_PACKETS = 1;
    const int QOS = 1;
    const bool MESSAGE_RETENTION = false;

    const char *CLIENT_ID = get_argument(argc, argv, "--client-id", 0, "client-001");
    const char *BROKER_HOST = get_argument(argc, argv, "--broker", 1, NULL);
    const int BROKER_PORT = atoi(get_argument(argc, argv, "--port", 1, NULL));
    const char *TOPIC = get_argument(argc, argv, "--topic", 1, NULL);
    const char *USERNAME = get_argument(argc, argv, "--username", 1, NULL);
    const char *PASSWORD = get_argument(argc, argv, "--password", 1, NULL);
    const char *DATA_FILE = get_argument(argc, argv, "--data-file", 1, NULL);
    const int MAX_MESSAGE_BYTES = atoi(get_argument(argc, argv, "--max-message-bytes", 0, "100"));
    const int READ_INTERVAL = atoi(get_argument(argc, argv, "--read-interval", 0, "5"));

    int status;
    char *message;
    int bytes;
    int running = 1;

    mosquitto_lib_init();

    mosquitto_client = mosquitto_new(CLIENT_ID, CLEAN_SESSION, NULL);

    mosquitto_username_pw_set(mosquitto_client, USERNAME, PASSWORD);

    status = mosquitto_connect(mosquitto_client, BROKER_HOST, BROKER_PORT, KEEPALIVE);

    if (status != SUCCESS_CODE) {
        printf("Client could not connect to the broker in: %s:%d.\n", BROKER_HOST, BROKER_PORT);
        printf("Error code: %d.\n", status);
        
        mosquitto_destroy(mosquitto_client);
        mosquitto_lib_cleanup();
        
        return ERROR_CODE;
    } 
    
    printf("Client connected to the broker in: %s:%d.\n", BROKER_HOST, BROKER_PORT);

    signal(SIGINT, signal_interrupt);

    while(running) {
        mosquitto_loop(mosquitto_client, TIMEOUT, MAX_PACKETS);

        message = read_data_file(DATA_FILE, MAX_MESSAGE_BYTES);

        if (message == NULL) {
            printf("Broker: %s | Port: %d | Status: Waiting for message | Message: NULL.\n", BROKER_HOST, BROKER_PORT);
        }
        else {
            bytes = strlen(message);

            status = mosquitto_publish(mosquitto_client, NULL, TOPIC, bytes, message, QOS, MESSAGE_RETENTION);
            
            if (status == SUCCESS_CODE) {
                printf("Broker: %s | Port: %d | Status: Sent | Message: %s.\n", BROKER_HOST, BROKER_PORT, message);
            } 
            else {
                printf("Broker: %s | Port: %d | Status: Error | Message: %s.\n", BROKER_HOST, BROKER_PORT, message);
            }
        }

        sleep(READ_INTERVAL);
    }
    
    return SUCCESS_CODE;
}