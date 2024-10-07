#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import argparse
import erppeek

from cfg_secret_configuration import (
    odoo_configuration_user_test as odoo_configuration_user,
)


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
    odoo_configuration_user["url"],
    odoo_configuration_user["login"],
    odoo_configuration_user["password"],
    odoo_configuration_user["database"],
)


###############################################################################
# Script
###############################################################################
def parse_args():
    parser = argparse.ArgumentParser(description="desc")
    parser.add_argument("var", help="desc")

    return parser.parse_args()


def main():
    # Configure arguments parser
    # args = parse_args()

    members = openerp.ResPartner.browse(
        [
            ("active", "=", True),
            ("is_worker_member", "=", True),
        ]
    )

    print("nom;email;service")
    for member in members:
        if member.is_squadleader is True:
            name = member.name
            email = member.email
            service = member.current_template_name
            print(f"{name};{email};{service}")


if __name__ == "__main__":
    main()
