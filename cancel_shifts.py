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

holiday_cache = {}

def create_holiday(name, date_begin, date_end):
    data = {
            "name": name,
            "holiday_type": 'single_day',
            "date_end": date_end,
            "date_begin": date_begin
            }
    holiday = openerp.ShiftHoliday.create(data)
    holiday.button_confirm()
    return openerp.ShiftHoliday.get(holiday.id)

def get_holiday(date):
    name = 'Fermeture ' + date
    h = None
    try:
        # Try to get ass from the cache
        h = holiday_cache[name]
    except:
        # Try to get ass from Odoo
        holidays = openerp.ShiftHoliday.browse([("name", "=", name)])
        if holidays is not None and len(holidays) > 0:
            h = holidays[0]
        else:
            # Create new ass
            try:
                h = create_holiday(name, date, date)
            except:
                return
        holiday_cache[name] = h
    return h

def main():
    # Configure arguments parser
    parser = argparse.ArgumentParser(
            description='Annule des services')
    parser.add_argument('--dry-run', dest='dry', default=False,
            action='store_true', help='Liste les services sans les annuler')
    parser.add_argument('--close-store', dest='closed', default=False,
            action='store_true', help='Ferme le magasin')
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
#            # Set nb ftop seats to 0 to avoid any registering
#            for ticket in shift.shift_ticket_ids:
#                if ticket.shift_type == 'ftop':
#                    ticket.seats_max = 0
#            # Cancel the shift
#            try:
#                shift.button_cancel()
#            except:
#                pass
            # Close the store to send email to registered members
            holiday = get_holiday(shift.date_without_time)
            shift.state_in_holiday = 'closed'

    # Confirm all holidays to trigger mail sending
    for holiday in holiday_cache.values():
        for s in filter(lambda x: (not x.state_in_holiday), holiday.single_day_shift_ids):
            s.state_in_holiday = 'open'
            print(s, s.state_in_holiday)
        holiday.button_done()

if __name__ == "__main__":
    main()
