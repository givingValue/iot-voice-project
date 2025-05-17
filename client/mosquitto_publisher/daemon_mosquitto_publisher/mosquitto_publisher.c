#include <stdbool.h>
#include <stdio.h>
#include <mosquitto.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <signal.h>
#include <systemd/sd-daemon.h>
#include <systemd/sd-journal.h>

#define LOG_BUFFER_SIZE 2048
#define LINE_BUFFER_SIZE 255
#define SOCKET_BUFFER_SIZE 1024
#define NOT_FOUND "not found"

const int SUCCESS_CODE = 0;
const int ERROR_CODE = -1;
const int ERROR_NUMBER = 1;
const bool CLEAN_SESSION = true;
const int KEEPALIVE = 60;
const int TIMEOUT = 1000;
const int MAX_PACKETS = 1;
const int QOS = 1;
const bool MESSAGE_RETENTION = false;
const char FILE_DELIMITER = '=';

char *CLIENT_ID;
char *BROKER_HOST;
int BROKER_PORT;
char *TOPIC;
char *USERNAME;
char *PASSWORD;
int MAX_MESSAGE_BYTES;
int READ_INTERVAL;
char *CONFIG_FILE_PATH;
char *LOG_FILE_PATH = "/var/log/mosquitto-publisher/mosquitto-publisher.log";

char log_message[LOG_BUFFER_SIZE];
sd_journal *journal;
struct mosquitto *mosquitto_client;

void write_log_in_file(char *log_message) {
    FILE *file;
    file = fopen(LOG_FILE_PATH, "a");
    fwrite(log_message , sizeof(char), strlen(log_message), file);
    fclose(file);
}

void logger(int level, char *log_message) {
    sd_journal_print(level, "%s", log_message);
    write_log_in_file(log_message);
}

char *copy_data_value(char *data_value, size_t length) {
    char *value = (char *)malloc(length + 1);
    strncpy(value, data_value, length);
    value[length] = '\0';
    return value;
}

char *get_argument_from_console(int arguments_length, char **arguments, char *argument_name) {
    char *argument_value = NOT_FOUND;
    char *console_argument_name;

    for(int index = 1; index < arguments_length; index++) {
        console_argument_name = arguments[index];

        if (strcmp(console_argument_name, argument_name) == 0) {
            argument_value = copy_data_value(arguments[index + 1], strlen(arguments[index + 1]));
            return argument_value;
        }

        if (index == arguments_length - 1) {
            return NOT_FOUND;
        }
    }

    return argument_value;
}

bool valid_config_line(char *line) {
    if ((line[0] == '#') || (line[0] == '\n')) {
        return false;
    } else {
        return true;
    }
}

char *get_argument_name_from_line(char *line, char delimiter) {
    char *argument_name = NOT_FOUND;
    char *rest;

    if ((rest = strchr(line, delimiter)) != NULL) {
        argument_name = copy_data_value(line, rest - line);
    }

    return argument_name;
}

char *get_argument_value_from_line(char *line, char delimiter) {
    char *argument_value;
    char *content;

    content = strchr(line, delimiter);
    content = content + 1;
    content[strcspn(content, "\n")] = 0;

    argument_value = copy_data_value(content, strlen(content));

    return argument_value;
}

char *get_argument_from_file(char *argument_name) {
    char *argument_value = NOT_FOUND;
    FILE *config_file;
    char *line_argument_name;
    char line[LINE_BUFFER_SIZE];

    config_file = fopen(CONFIG_FILE_PATH, "r");

    while (fgets(line, LINE_BUFFER_SIZE, config_file) != NULL) {
        if (valid_config_line(line)) {
            line_argument_name = get_argument_name_from_line(line, FILE_DELIMITER);
            if (strcmp(line_argument_name, argument_name) == 0) {
                free(line_argument_name);
                argument_value = get_argument_value_from_line(line, FILE_DELIMITER);
                break;
            }
        }
    }

    fclose(config_file);

    return argument_value;
}

char *get_argument(int arguments_length, char **arguments, char *argument_console_name, char *argument_file_name, bool check_config_file, bool required, char *default_value) {
    char *argument_value = get_argument_from_console(arguments_length, arguments, argument_console_name);

    if (strcmp(argument_value, NOT_FOUND) != 0) {
        return argument_value;
    }

    if (check_config_file) {
        argument_value = get_argument_from_file(argument_file_name);

        if (strcmp(argument_value, NOT_FOUND) != 0) {
            return argument_value;
        }
    }

    if ((strcmp(argument_value, NOT_FOUND) == 0) && (default_value)) {
        return default_value;
    }

    if ((strcmp(argument_value, NOT_FOUND) == 0) && (required)) {
        snprintf(log_message, LOG_BUFFER_SIZE, "The argument %s|%s must be provided through the command line or a configuration file.\n", argument_console_name, argument_file_name);
        logger(LOG_ERR, log_message);
        sd_notifyf(0, "STATUS=Failed to start up: %s.\nERRNO=%i", log_message, ERROR_NUMBER);
        exit(ERROR_CODE);
    }
}

int verify_if_config_file(int arguments_length, char **arguments) {
    FILE *file;
    int config_file = 1;

    CONFIG_FILE_PATH = get_argument_from_console(arguments_length, arguments, "--config-file");

    if (strcmp(CONFIG_FILE_PATH, NOT_FOUND) == 0) {
        return 0;
    }

    file = fopen(CONFIG_FILE_PATH, "r");

    if (file == NULL) {
        snprintf(log_message, LOG_BUFFER_SIZE, "The config file: %s does not exist.\n", CONFIG_FILE_PATH);
        logger(LOG_ERR, log_message);
        sd_notifyf(0, "STATUS=Failed to start up: %s.\nERRNO=%i", log_message, ERROR_NUMBER);
        exit(ERROR_CODE);
    } else {
        fclose(file);
    }

    return config_file;
}

void set_arguments(int arguments_length, char **arguments, bool check_config_file, bool reloading) {

    if ((arguments_length <= 1) && (!reloading)) {
        snprintf(log_message, LOG_BUFFER_SIZE, "There are not arguments.\n");
        logger(LOG_ERR, log_message);
        sd_notifyf(0, "STATUS=Failed to start up: %s.\nERRNO=%i", log_message, ERROR_NUMBER);
        exit(ERROR_CODE);
    }

    CLIENT_ID = get_argument(arguments_length, arguments, "--client-id", "CLIENT_ID", check_config_file, 0, "client-001");
    BROKER_HOST = get_argument(arguments_length, arguments, "--broker", "BROKER", check_config_file, 1, NULL);
    BROKER_PORT = atoi(get_argument(arguments_length, arguments, "--port", "PORT", check_config_file, 1, NULL));
    TOPIC = get_argument(arguments_length, arguments, "--topic", "TOPIC", check_config_file, 1, NULL);
    USERNAME = get_argument(arguments_length, arguments, "--username", "USERNAME", check_config_file, 1, NULL);
    PASSWORD = get_argument(arguments_length, arguments, "--password", "PASSWORD", check_config_file, 1, NULL);
    MAX_MESSAGE_BYTES = atoi(get_argument(arguments_length, arguments, "--max-message-bytes", "MAX_MESSAGE_BYTES", check_config_file, 0, "100"));
    READ_INTERVAL = atoi(get_argument(arguments_length, arguments, "--read-interval", "READ_INTERVAL", check_config_file, 0, "5"));
}

int get_socket_file_descriptor() {
    char **file_descriptors_names = NULL;
    int file_descriptors_length;
    int socket_file_descriptor = -1;
    int error = 0;
    int is_socket_unix;

    file_descriptors_length = sd_listen_fds_with_names(0, &file_descriptors_names);

    if(file_descriptors_length < 0) {
        error = 1;
    }

    if(file_descriptors_length == 0 || file_descriptors_names == NULL){
        error = 1;
    }

    for(int i=0; i < file_descriptors_length; i++) {
        is_socket_unix = sd_is_socket_unix(i + SD_LISTEN_FDS_START, SOCK_DGRAM, -1, (const char*) file_descriptors_names[i], strlen(file_descriptors_names[i]));
        if(is_socket_unix > 0){
            logger(LOG_INFO, "Mosquitto publisher socket found.");
            socket_file_descriptor = i + SD_LISTEN_FDS_START;
            error = 0;
            break;
        } else {
            error = 1;
        }
    }

    free(file_descriptors_names);

    if (error) {
        snprintf(log_message, LOG_BUFFER_SIZE, "Mosquitto publisher socket not found.\n");
        logger(LOG_ERR, log_message);
        sd_notifyf(0, "STATUS=Failed to start up: %s.\nERRNO=%i", log_message, ERROR_NUMBER);
        exit(ERROR_CODE);
    }

    return socket_file_descriptor;
}

void config_mosquitto_client() {
    mosquitto_lib_init();

    mosquitto_client = mosquitto_new(CLIENT_ID, CLEAN_SESSION, NULL);

    mosquitto_username_pw_set(mosquitto_client, USERNAME, PASSWORD);

    int status = mosquitto_connect(mosquitto_client, BROKER_HOST, BROKER_PORT, KEEPALIVE);

    if (status != SUCCESS_CODE) {
        snprintf(log_message, LOG_BUFFER_SIZE, "Mosquitto publisher could not connect to the broker in: %s:%d.\n", BROKER_HOST, BROKER_PORT);
        logger(LOG_ERR, log_message);
        snprintf(log_message, LOG_BUFFER_SIZE, "Error code: %d.\n", status);
        logger(LOG_ERR, log_message);

        mosquitto_destroy(mosquitto_client);
        mosquitto_lib_cleanup();

        sd_notifyf(0, "STATUS=Failed to start up: %s.\nERRNO=%i", log_message, ERROR_NUMBER);
        exit(ERROR_CODE);
    }

    snprintf(log_message, LOG_BUFFER_SIZE, "Mosquitto publisher connected to the broker in: %s:%d.\n", BROKER_HOST, BROKER_PORT);
    logger(LOG_INFO, log_message);
}

void reload(int sig) {
    logger(LOG_NOTICE, "Mosquitto publisher is reloading.\n");
    sd_notifyf(0, "RELOADING=1\n STATUS=Reloading Configuration\n MAINPID=%lu", (unsigned long) getpid());

    mosquitto_disconnect(mosquitto_client);
    mosquitto_destroy(mosquitto_client);
    mosquitto_lib_cleanup();

    set_arguments(0, NULL, 1, 1);

    config_mosquitto_client();

    logger(LOG_NOTICE, "Mosquitto publisher is reloaded.\n");
    sd_notify(0, "READY=1\nSTATUS=Ready\n");
}

void interrupt(int sig) {
    mosquitto_disconnect(mosquitto_client);
    mosquitto_destroy(mosquitto_client);
    mosquitto_lib_cleanup();

    logger(LOG_NOTICE, "Mosquitto publisher interrupted.\n");
    exit(SUCCESS_CODE);
}

int main(int argc, char **argv){
    int status;
    int running = 1;
    int check_config_file;
    int socket_file_descriptor;
    ssize_t socket_recieved_bytes;
    char socket_buffer[SOCKET_BUFFER_SIZE];

    socket_file_descriptor = get_socket_file_descriptor();

    check_config_file = verify_if_config_file(argc, argv);
    set_arguments(argc, argv, check_config_file, 0);

    config_mosquitto_client();

    signal(SIGINT, interrupt);
    signal(SIGTERM, interrupt);
    signal(SIGHUP, reload);

    sd_journal_open(&journal, 0);

    logger(LOG_INFO, "Mosquitto publisher initiated.\n");
    sd_notify(0, "READY=1");

    while(running) {
        mosquitto_loop(mosquitto_client, TIMEOUT, MAX_PACKETS);

        socket_recieved_bytes = recv(socket_file_descriptor, socket_buffer, SOCKET_BUFFER_SIZE - 1, MSG_DONTWAIT);

        if (socket_recieved_bytes > 0) {
            socket_buffer[socket_recieved_bytes] = '\0';
            status = mosquitto_publish(mosquitto_client, NULL, TOPIC, socket_recieved_bytes, socket_buffer, QOS, MESSAGE_RETENTION);

            if (status == SUCCESS_CODE) {
                snprintf(log_message, LOG_BUFFER_SIZE, "Broker: %s | Port: %d | Topic: %s | Status: Sent | Message: %s.\n", BROKER_HOST, BROKER_PORT, TOPIC, socket_buffer);
                logger(LOG_INFO, log_message);
            }
            else {
                snprintf(log_message, LOG_BUFFER_SIZE, "Broker: %s | Port: %d | Topic: %s | Status: Error | Message: %s.\n", BROKER_HOST, BROKER_PORT, TOPIC, socket_buffer);
                logger(LOG_ERR, log_message);
            }
        } else {
            snprintf(log_message, LOG_BUFFER_SIZE, "Broker: %s | Port: %d | Topic: %s | Status: Waiting for message | Message: NULL.\n", BROKER_HOST, BROKER_PORT, TOPIC);
            logger(LOG_INFO, log_message);
        }

        sleep(READ_INTERVAL);
    }

    return SUCCESS_CODE;
}
