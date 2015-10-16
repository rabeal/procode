#!/bin/bash

sudo pkill supervisor
sudo pkill gunicorn
sudo supervisord -c simple.conf

echo "Updated version ready."
