#!/bin/bash
USER=`whoami`
SCRIPT_DIR=$(dirname "$0")
date=`date +%d-%m-%Y`

journalctl --since "today" --no-pager > /var/log/daily_log_report_$date.txt
grep -E -v '(usb|UFW|mtp-probe|rtkit|baloo|NetworkManager|dbus-daemon|telegram)' /var/log/daily_log_report_$date.txt > $SCRIPT_DIR/./../data/daily_log_report.txt
chown $USER:$USER $SCRIPT_DIR/./../data/daily_log_report.txt


# test run
# grep -E -v '(usb|UFW|mtp-probe|rtkit|baloo|NetworkManager|dbus-daemon|telegram)' /var/log/daily_log_report_$date.txt | head -n 50 > $SCRIPT_DIR/daily_log_report.txt