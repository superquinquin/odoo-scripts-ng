#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import erppeek
import argparse

from cfg_secret_configuration\
        import odoo_configuration_user_prod as odoo_configuration_user

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
# Configuration
###############################################################################

###############################################################################
# Script
###############################################################################
def create_counter_event(shift_type, partner_id, point_qty, name, note):
    new_event_data = {
            "name": name,
            "partner_id": partner_id,
            "type": shift_type,
            "point_qty": point_qty,
            "notes": note
            }
    new_event = openerp.ShiftCounterEvent.create(new_event_data)
    new_event.write(new_event_data)

def reset_member_counters(member):
    event_name = "Remise à zéro compteur"
    event_note = "Incitation au retour des desinscrits"
    if member.final_standard_point < 0:
        create_counter_event("standard", member.id,
                             0-member.final_standard_point,
                             event_name, event_note)
    if member.final_ftop_point < 0:
        create_counter_event("ftop", member.id, 0-member.final_ftop_point,
                             event_name, event_note)

def main():
    # Configure arguments parser
    parser = argparse.ArgumentParser(
            description='Remet les compteurs à 0')

    args = parser.parse_args()

    count=0
    for member in openerp.ResPartner.browse(
            [("is_worker_member", "=", True),
             ("active", "=", True),
             ("is_unsubscribed", "=", True),
             ("unsubscription_date", ">=", "2022-01-01"),
             ("unsubscription_date", "<=", "2022-06-30")]):
        count+=1
        print (member.name, member.shift_type, member.working_state,
            member.unsubscription_date, member.final_standard_point,
               member.final_ftop_point)
        reset_member_counters(member)

    print("Found", count, "members")

if __name__ == "__main__":
    main()
