#!/usr/bin/env python
"""
This script is a prototype of a ssl monitoring system.
It checks for the expiration date and alerts whether cert is
1. Expired
2. About to expire in 2 weeks
3. Valid, with the expiration date

Script uses asyncio to speed up checking hostnames simultaneously.
"""

import datetime
import socket
import ssl
import asyncio
import argparse
import logging

TIME_ERROR = datetime.datetime.utcnow()

c = (
    "\033[0m",  # End of color
    "\033[36m",  # Cyan
    "\033[91m",  # Red
    "\033[35m",  # Magenta
)


class InvalidHostException(Exception):
    pass

def ssl_expiry_datetime(hostname):
    """
    Main function that checks SSL certificate on the given hostname.
    """
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET),
                               server_hostname=hostname)
    try:
        conn.connect((hostname, 443))
        ssl_info = conn.getpeercert()
        # Parse the string from the certificate into a Python datetime object
        return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
    except (ssl.SSLError, socket.gaierror, socket.timeout,
            socket.error) as error:
        logging.error('%s%s: %s%s', c[3], hostname, error, c[0])
        raise InvalidHostException from error


async def ssl_valid_time_remaining(hostname, nocol, buffer_days=14):
    """
    Get the number of days left in a cert's lifetime.
    """
    try:
        expires = ssl_expiry_datetime(hostname)
        logging.debug('SSL certificate for %s expires at %s', hostname, expires)
    except InvalidHostException as error:
        logging.error('%s%s: %s%s', c[3], hostname, error, c[0])
        return []
    remaining = expires - datetime.datetime.utcnow()
    if remaining < datetime.timedelta(days=0):
        print(f"{c[0] if nocol else c[3]}{hostname}: Expired{c[0]}")
    elif remaining < datetime.timedelta(days=buffer_days):
        print(
            f"{c[0] if nocol else c[2]}{hostname}: {remaining.days}. Expiring in {buffer_days} days.{c[0]}"
        )
    else:
        print(f"{c[0] if nocol else c[1]}{hostname}: {remaining.days}{c[0]}")

    return [hostname, remaining]


async def ssl_expires_in(hostnames, nocol=False):
    """
    Asyncio function starting point.
    """
    await asyncio.gather(*(ssl_valid_time_remaining(hostname, nocol)
                           for hostname in hostnames))
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--no-color', action='store_true')
    parser.add_argument('--expiry-time')  # Specify expiry buffer time
    parser.add_argument(
        '--only-expired-hosts')  # List only hosts with expired certificates

    args, rest = parser.parse_known_args()
    log_level = logging.ERROR
    if args.debug:
        log_level = logging.DEBUG
    if args.verbose:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s %(message)s')
    try:
        for hostfile in rest:
            try:
                with open(hostfile, encoding='utf-8') as F:
                    hosts = F.read()
                    hostlist = hosts.split('\n')
                    logging.debug('Hosts = %s', hostlist)
                    hostlist.remove('')
                if args.no_color:
                    asyncio.run(ssl_expires_in(hostlist, True))
                else:
                    asyncio.run(ssl_expires_in(hostlist))
            except FileNotFoundError:
                logging.error('Host file %s not found.', hostfile)
    except KeyboardInterrupt:
        pass
