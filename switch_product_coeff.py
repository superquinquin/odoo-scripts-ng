#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import argparse
from typing import cast
import erppeek

from cfg_secret_configuration import (
    odoo_configuration_user_prod as odoo_configuration_user,
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
    parser.add_argument("current", help="The current coeff id")
    parser.add_argument("target", help="The target coeff id")
    parser.add_argument(
        "--only-categ",
        help='Select categories to apply switch to (ex: "id1,id2,id3")',
        type=str,
        dest="only_categ",
        nargs="?",
    )
    parser.add_argument(
        "--dry-run",
        help="Only show what's going to be done",
        action="store_true",
        dest="dry_run",
        default=False,
    )

    return parser.parse_args()


def switch_coeff(
    product: erppeek.Record,
    cur_coeff: int,
    tgt_coeff: int,
    dry_run: bool = False,
):
    for id in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        coeff_key = f"coeff{id}_id"
        coeff = product.read(coeff_key)
        if coeff and coeff.id == int(cur_coeff):
            print(f"{product.name}: Ready to switch coeff on id {coeff_key}")
            if not dry_run:
                try:
                    product.write({coeff_key: tgt_coeff})
                    print("ok")
                except Exception as e:
                    print(f"*** FAILED *** ({e})")


def main():
    # Configure arguments parser
    args = parse_args()

    model = cast(erppeek.Model, openerp.ProductTemplate)
    filter = []
    # filter.append(("id", "=", 10025))

    if args.only_categ is not None:
        categs = [int(x) for x in args.only_categ.split(",")]
        filter.append(("categ_id", "in", categs))

    products = cast(erppeek.RecordList, model.browse(filter))
    for product in products:
        switch_coeff(
            cast(erppeek.Record, product),
            args.current,
            args.target,
            args.dry_run,
        )


if __name__ == "__main__":
    main()
