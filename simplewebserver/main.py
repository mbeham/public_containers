#!/usr/bin/env python


import logging
import os
import sys
import random
import time

import tornado.ioloop
import tornado.web
from tornado.escape import json_encode


PORT = os.getenv("PORT", 8080)
VERSION = os.getenv("VERSION", "1.0.1")

HEALTH_MIN = os.getenv('HEALTH_MIN', 0)
HEALTH_MAX = os.getenv('HEALTH_MAX', 0)

SLOW = int(os.getenv('SLOW', 0))

HOSTNAME = os.getenv('HOSTNAME', 'unknown_hostname')
DEBUG = True

if DEBUG:
    FORMAT = "%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt="%Y-%m-%dT%I:%M:%S")
else:
    FORMAT = "%(asctime)-0s %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%dT%I:%M:%S")


class Endpoint0(tornado.web.RequestHandler):
    def get(self):
        """
        Handles `/endpoint0` resource.
        """
        try:
            logging.info("/endpoint0 serving from %s has been invoked from %s", self.request.host, self.request.remote_ip)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(
                {
                    "version" : VERSION,
                    "host" : HOSTNAME,
                    "result" : "all is well"
                }
            ))
            self.finish()
        except Exception as e:
            logging.debug(e)
            self.set_status(404)


class Health(tornado.web.RequestHandler):
    def get(self):
        """
        Handles `/health` resource.
        """
        try:
            logging.info("/health serving from %s has been invoked from %s", self.request.host, self.request.remote_ip)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(
                {
                    "healthy" : True
                }
            ))

            if HEALTH_MAX > HEALTH_MIN and HEALTH_MIN >= 0: # make sure no shenanigans take place
                delay_response = random.randrange(float(HEALTH_MIN), float(HEALTH_MAX))
                time.sleep(delay_response/1000.0)
            self.finish()
        except Exception as e:
            logging.debug(e)
            self.set_status(404)


class Info(tornado.web.RequestHandler):
    def get(self):
        try:
            logging.info("/info serving from %s has been invoked from %s", self.request.host, self.request.remote_ip)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(
                {
                    "version" : VERSION,
                    "host" : self.request.host,
                    "hostname": HOSTNAME,
                    "from" : self.request.remote_ip
                }
            ))
            self.finish()
        except Exception as e:
            logging.debug(e)
            self.set_status(404)


class Env(tornado.web.RequestHandler):
    def get(self):
        try:
            logging.info("/env serving from %s has been invoked from %s", self.request.host, self.request.remote_ip)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(
                {
                    "version" : VERSION,
                    "env" : str(os.environ),
                }
            ))
            self.finish()
        except Exception as e:
            logging.debug(e)
            self.set_status(404)


class Kill(tornado.web.RequestHandler):

    def get(self):
        logging.info("Termination requested. Doing (simulated) cleanup")
        sys.exit(0)


class Secrets(tornado.web.RequestHandler):

    def get(self):
        try:
            logging.info("/secrets serving from %s has been invoked from %s", self.request.host, self.request.remote_ip)
            self.set_header("Content-Type", "application/json")

            result = []
            for root, dirs, files in os.walk('/var/run/secrets'):
                for file in files:
                    result.append(os.path.join(root, file))
                for dir in dirs:
                    result.append(os.path.join(root, dir))

            for root, dirs, files in os.walk('/config'):
                for file in files:
                    result.append(os.path.join(root, file))
                for dir in dirs:
                    result.append(os.path.join(root, dir))

            for root, dirs, files in os.walk('/secrets'):
                for file in files:
                    result.append(os.path.join(root, file))
                for dir in dirs:
                    result.append(os.path.join(root, dir))

            result.sort()

            self.write(json_encode(
                {
                    "version" : VERSION,
                    "secrets" : result
                }
            ))
            self.finish()
        except Exception as e:
            logging.debug(e)
            self.set_status(404)


if __name__ == "__main__":
    if SLOW > 0:
        time.sleep(SLOW)

    app = tornado.web.Application([
        (r"/", Endpoint0),
        (r"/endpoint", Endpoint0),
        (r"/health", Health),
        (r"/info", Info),
        (r"/env", Env),
        (r"/kill", Kill),
        (r"/secrets", Secrets)
    ])
    app.listen(PORT, address='0.0.0.0')
    logging.info("Simple service (version v%s) listening in port %s", VERSION, PORT)
    tornado.ioloop.IOLoop.current().start()
