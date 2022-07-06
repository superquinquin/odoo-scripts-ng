#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import argparse
import erppeek

from cfg_secret_configuration import odoo_configuration_user_test as odoo_configuration_user

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
# Script
###############################################################################
def parse_args():
    parser = argparse.ArgumentParser(
            description='Set specific max and min seats on shift templates')
    parser.add_argument('total_max', help='The total max number of seats')
    parser.add_argument('abcd_max', help='The max number of abcd seats')
    parser.add_argument('ftop_max', help='The max number of ftop seats')

    return parser.parse_args()

def set_max_limits(shift, total_max, abcd_max, ftop_max):
    shift.seats_max = total_max
    print(shift.name, shift.day, shift.seats_availability, shift.seats_max)
    for ticket in shift.shift_ticket_ids:                                       
        if ticket.shift_type == 'standard':
            ticket.seats_max = abcd_max
        elif ticket.shift_type == 'ftop':
            ticket.seats_max = ftop_max
        print(ticket.shift_type, ticket.seats_max) 

def main():
    # Configure arguments parser
    args = parse_args()

    shift_templates = openerp.ShiftTemplate.browse([
        ("active", "=", True),
        ("shift_type_id", "=", 1),
        ("tu", "=", False)
        ])
    for tmpl in shift_templates:
        print(tmpl, tmpl.shift_type_id)
        set_max_limits(tmpl, args.total_max, args.abcd_max, args.ftop_max)

if __name__ == "__main__":
    main()
