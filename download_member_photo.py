#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import argparse
import erppeek
from typing import cast
import base64

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
    parser.add_argument(
        "name", help="Name of member in the form NAME, surname"
    )

    return parser.parse_args()


def main():
    # Configure arguments parser
    args = parse_args()

    model = cast(erppeek.Model, openerp.ResPartner)
    filter = [("name", "=", args.name)]

    members = cast(erppeek.RecordList, model.browse(filter))
    for member in members:
        img_file = open(f"{args.name}.txt", "w")
        img_file.write(member.image)
        img_file.close()


if __name__ == "__main__":
    main()
