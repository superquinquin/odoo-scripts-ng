#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import erppeek

from enum import Enum
from date_tools import conflict_period
from datetime import datetime

from cfg_secret_configuration import odoo_configuration_user_test as odoo_configuration_user

class CounterType(Enum):
    FTOP = "ftop"
    STANDARD = "standard"


###############################################################################
# Odoo Connection
###############################################################################
def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz

openerp, uid, tz = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])

###############################################################################
# Script
###############################################################################

DATE_FORMAT = '%Y-%m-%d'

def is_member_exempted(member, date_cycle_begin, date_cycle_end):
    conflict = False
    for leave in filter(
            lambda l: l.state == 'done', member.leave_ids):
        conflict = conflict or conflict_period(
                leave.start_date,
                leave.stop_date,
                date_cycle_begin,
                date_cycle_end, True)['conflict']
    return conflict

def is_member_flying(member):
    stype = member.shift_type
    if stype in "ftop":
        return True
    return False

def is_member_fixed(member):
    stype = member.shift_type
    if stype in "standard":
        return True
    return False

def member_subscription_date(member):
    oldest_invoice_date = datetime.today()
    for invoice in openerp.AccountInvoice.browse([
            ("partner_id", "=", member.id),
            ("is_capital_fundraising", "=", True),
            ("state", "=", "paid"),
            ("date_invoice", "!=", False)]):
        invoice_date = datetime.strptime(invoice.date_invoice, DATE_FORMAT)
        if invoice_date < oldest_invoice_date:
            oldest_invoice_date = invoice_date
    return oldest_invoice_date

def get_nb_shift_done(member, date_attendance_rec_begin, date_attendance_rec_end):
    counters = openerp.ShiftCounterEvent.browse(
            [("partner_id", "=", member.id),
                ("type", "=", "ftop"),
                ("create_date", ">=", date_attendance_rec_begin),
                ("create_date", "<=", date_attendance_rec_end),
                ("point_qty", "=", 1)
                ]
            )
    if counters is not None:
        return len(counters)
    return 0

def calc_new_counter_value(counter_type, member, point_qty):
    current_points = 0
    if counter_type is CounterType.FTOP:
        current_points = member.read('final_ftop_point')
    elif counter_type is CounterType.STANDARD:
        current_points = member.read('final_standard_point')

    return current_points + point_qty

def add_counter_event(counter_type, member, point_qty, name, note,
        dry_run=True):

    new_counter_value = calc_new_counter_value(counter_type, member, point_qty)

    if dry_run is False:
        new_event_data = {
                "name": name,
                "partner_id": member.id,
                "type": counter_type.value,
                "point_qty": point_qty,
                "notes": note
                }
        new_event = openerp.ShiftCounterEvent.create(new_event_data)
        new_event.write(new_event_data)

    return new_counter_value



#
# Close shift cycle for a member
#
# Return the new state of the member (if changed)
# 
def close_cycle(member, date_cycle_begin, date_cycle_end,
        date_attendance_rec_begin, date_attendance_rec_end, nb_cycle,
        dry_run=True):

    counter_event_name = "Cloture cycle ABCD %s" % datetime.strptime(date_cycle_end, DATE_FORMAT).strftime("%d/%m/%Y")
    new_counter_val = 0
    old_ftop_counter_val = member.read('final_ftop_point')
    old_standard_counter_val = member.read('final_standard_point')

    # If member subscribed to sqq during the cycle => exempted
    if member_subscription_date(member) > datetime.strptime(date_cycle_begin, DATE_FORMAT):
        return 0

    # If member was on vacation of any kind => exempted
    if is_member_exempted(member, date_cycle_begin, date_cycle_end):
        return 0
    
    # Special treatmemt for ftop members
    if is_member_flying(member):
        new_counter_val = add_counter_event(CounterType.FTOP, member, - nb_cycle,
                counter_event_name,
                "Soustraction auto d'un point à un membre volant", dry_run)
    # Special treatment for fixed members
    elif is_member_fixed(member):
        nb_shift = get_nb_shift_done(member, date_attendance_rec_begin,
                date_attendance_rec_end)
        # Member attended at least one shift per cycle
        if nb_shift >= nb_cycle:
            add_counter_event(CounterType.FTOP, member, - nb_cycle,
                    counter_event_name,
                    "Soustraction auto des points vacation à un membre fixe",
                    dry_run)
            # If member was not "up to date" increment its standard counter
            std_point = member.read('final_standard_point')
            if std_point < 0:
                max_point = min(- std_point, nb_cycle)
                new_counter_val = add_counter_event(CounterType.STANDARD,
                        member, max_point, counter_event_name,
                        ("Membre fixe en alerte/suspendu + Présence à au moins"
                            "1 service pendant ce cycle => Ajout d'un point"
                            "standard"), dry_run)
        # Member did not attend enough shifts during cycle(s)
        else:
            available_ftop_points = member.read('final_ftop_point')
            # If member has some points on its ftop counter,
            #   use these to compensate
            if available_ftop_points > 0:
                points_to_remove = min(available_ftop_points, nb_cycle)
                remaining_points = nb_cycle - points_to_remove
                add_counter_event(CounterType.FTOP, member, - points_to_remove,
                        counter_event_name,
                        ("Membre fixe absent pendant ce cycle + Compteur"
                            "vacation > 0 => Soustraction de points vacation"),
                        dry_run)
                # If still remaining_points, remove them from standard counter
                if remaining_points > 0:
                    new_counter_val = add_counter_event(CounterType.STANDARD,
                            member, - remaining_points, counter_event_name,
                            ("Membre fixe absent pendant ce cycle + Compteur"
                                "vacation = 0 => Soustraction de points standard"),
                            dry_run)
            else:
                new_counter_val = add_counter_event(CounterType.STANDARD,
                        member, - nb_cycle, counter_event_name,
                        ("Membre fixe absent pendant ce cycle + Compteur"
                            "vacation = 0 => Soustraction de points standard"),
                        dry_run)

        # Check if member state changed
        old_counter_val = 0
        if is_member_flying(member):
            old_counter_val = old_ftop_counter_val
        else:
            old_counter_val = old_standard_counter_val

        if old_counter_val >= 0 and new_counter_val < 0:
            return 1
        else:
            return 0


def main(cycle_dates, nb_cycle=1, dry_run=False):

    date_cycle_begin = cycle_dates['date_cycle_begin']
    date_cycle_end = cycle_dates['date_cycle_end']
    date_attendance_rec_begin = cycle_dates['date_attendance_rec_begin']
    date_attendance_rec_end = cycle_dates['date_attendance_rec_end']

    count = 0
    for member in openerp.ResPartner.browse([
        ("active", "=", True),
        ("is_worker_member", "=", True),
        ("is_unsubscribed", "=", False)]):
        count +=1
        state_changed = close_cycle(member, date_cycle_begin, date_cycle_end,
                date_attendance_rec_begin, date_attendance_rec_end, nb_cycle,
                dry_run)
        print("%s => %s" % (member.name, "ALERTE" if state_changed == 1 else "ok"))

    print("%d members" % count)

def test_member(name, cycle_dates):
    date_cycle_begin = cycle_dates['date_cycle_begin']
    date_cycle_end = cycle_dates['date_cycle_end']
    date_attendance_rec_begin = cycle_dates['date_attendance_rec_begin']
    date_attendance_rec_end = cycle_dates['date_attendance_rec_end']

    for member in openerp.ResPartner.browse([("name", "=", name)]):
        print(member_subscription_date(member))
        if is_member_flying(member):
            print("Member %s is flying" % member.name)
        if is_member_fixed(member):
            print("Member %s is fixed" % member.name)
        if is_member_exempted(member, date_cycle_begin, date_cycle_end):
            print("Member %s is exempted" % member.name)
        print("Number of shifts attended: %d" % get_nb_shift_done(member, date_attendance_rec_begin, date_attendance_rec_end))
        state_changed = close_cycle(member, date_cycle_begin, date_cycle_end,
                date_attendance_rec_begin, date_attendance_rec_end, 2, False)
        print("%s => %s" % (member.name, "ALERTE" if state_changed == 1 else "ok"))

if __name__ == "__main__":
    # Cycle start & end date
    nb_cycle = 2
    dry_run = False
    cycle_dates = {
            'date_cycle_begin': '2021-07-05',
            'date_cycle_end': '2021-08-28',
            'date_attendance_rec_begin': '2021-07-09',
            'date_attendance_rec_end': '2021-08-30'
        }
    main(cycle_dates, nb_cycle, dry_run)
    #test_member("SAMNEANG, Anny", cycle_dates)
