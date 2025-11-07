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
    openerp.login(login, password=password, database=database)
    return openerp


openerp = init_openerp(
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

    shifts = openerp.ShiftTemplate.browse([("active", "=", True)])
    for s in shifts:
        leaders = list(map(lambda x: x.name, s.user_ids))
        print(f"{s.name} => {'+'.join(leaders)}")


if __name__ == "__main__":
    main()
