#!/bin/sh
gunicorn -b 0.0.0.0:9500 -k flask_sockets.worker totemlogs.server:app