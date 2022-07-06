#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import argparse
import erppeek
import csv
import unidecode
import traceback
from datetime import datetime
from dateutil import tz

from cfg_secret_configuration\
        import odoo_configuration_user_test as odoo_configuration_user

###############################################################################
# Odoo Connection
###############################################################################
def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz

openerp, uid, _ = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])


###############################################################################
# Configuration
###############################################################################

###############################################################################
# Script
###############################################################################
date_begin = "2021-06-07"
date_end = "2021-08-29"

def main():
    # Configure arguments parser
    parser = argparse.ArgumentParser(
            description='Annule des services')
    parser.add_argument('--dry-run', dest='dry', default=False,
            action='store_true', help='Liste les services sans les annuler')
    parser.add_argument('begin',
            help='Date de début (14/07/2022)')
    parser.add_argument('end',
            help='Date de fin (14/07/2022)')
    parser.add_argument('filter', nargs='?', default='',
            help='Heure du service à annuler chaque jour (08:45)')
    args = parser.parse_args()

    # Check arg format
    date_begin = None
    date_end = None
    try:
        date_begin = datetime.strptime(args.begin, '%d/%m/%Y').\
                replace(tzinfo = tz.tzlocal())
        date_end = datetime.strptime(args.end, '%d/%m/%Y').\
                replace(tzinfo = tz.tzlocal())
    except Exception as e:
        raise Exception('Mauvais format de date (JJ/MM/AAAA)')

    for shift in openerp.ShiftShift.browse(
            [("active", "=", True),
                "&",
                ("date_begin", ">=", date_begin),
                ("date_begin", "<=", date_end)
            ]):
        # Apply time filter if set
        if args.filter != '' and not shift.begin_date_string.endswith(args.filter):
            continue
        print(shift)
        if (not args.dry):
            for ticket in shift.shift_ticket_ids:
                if ticket.shift_type == 'ftop':
                    ticket.seats_max = 0
                    print(ticket.available_seat_ftop)
            try:
                shift.button_cancel()
            except:
                pass

if __name__ == "__main__":
    main()
