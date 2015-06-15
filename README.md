# Nagios-Check for monitoring your untis-powered timetables
## Notice
This notified me ony on events like cancelled lessons or substitution
## Configuration-Example
Service:
```
define service{
        host_name               localhost
        service_description     BLA-0000
        check_command           check_webuntis!USER!PASSWORD!SCHOOLNAME!CLASS!https://poly.webuntis.com/WebUntis/jsonrpc.do
        max_check_attempts      1
        check_interval          61
        retry_interval          30
        check_period            24x7
        notification_interval   61
        notification_period     24x7
        notification_options    w,c
        contacts                ich
}
```

Command
```
define command{
        command_name    check_webuntis
        command_line    $USER1$/stunden.py -u $ARG1$ -p $ARG2$ -n $ARG3$ -k $ARG4$ -s $ARG5$
}
```
