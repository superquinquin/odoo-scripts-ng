#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import argparse
import erppeek

from cfg_secret_configuration import odoo_configuration_user_prod as odoo_configuration_user

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
    parser.add_argument('--fill-ftop-to-max', dest='ftop_to_max',
                        default=False, action='store_true')

    return parser.parse_args()


def get_standard_available_seats(shift):
    avail_seats = 0
    for ticket in shift.shift_ticket_ids:
        if ticket.shift_type == 'standard':
            avail_seats = ticket.seats_available
            return avail_seats


def reset_ftop_seats(shift):
    for ticket in shift.shift_ticket_ids:
        if ticket.shift_type == 'ftop':
            ticket.seats_max = 0


def set_total_max(shift, total_max):
    try:
        shift.seats_max = total_max
    except:
        pass


def set_max_limits(shift, total_max, abcd_max, ftop_max, ftop_to_max):
    # Reset ftop seats
    reset_ftop_seats(shift)
    # Get available standard seats
    abcd_avail = get_standard_available_seats(shift)

    for ticket in shift.shift_ticket_ids:
        if ticket.shift_type == 'standard':
            ticket.seats_max = abcd_max
        elif ticket.shift_type == 'ftop':
            if ftop_to_max:
                ticket.seats_max = (total_max - abcd_max) + abcd_avail
            else:
                ticket.seats_max = ftop_max
        print(ticket.shift_type, ticket.seats_max)

    # Set total max seats for shift
    set_total_max(shift, total_max)

    print(shift.name, shift.day, shift.seats_availability, shift.seats_max)


def main():
    # Configure arguments parser
    args = parse_args()
    print(args.ftop_to_max)

    shifts = openerp.ShiftShift.browse([
        ("active", "=", True),
        ("shift_type_id", "=", 1),
        ("date_begin", ">=", "2024-07-15"),
        ("date_end", "<=", "2024-08-17"),
        ("begin_time", "=", 13.75)
    ])
    for shift in shifts:
        print(shift, shift.shift_type_id)
        # set_max_limits(shift, int(args.total_max), int(args.abcd_max),
        #                int(args.ftop_max), args.ftop_to_max)
        set_total_max(shift, 0)


if __name__ == "__main__":
    main()
    # tmpl = openerp.ShiftTemplate.get(147)
    # set_max_limits(tmpl, 12, 8, 0, True)
