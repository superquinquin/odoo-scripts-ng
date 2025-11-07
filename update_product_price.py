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
            description='desc')
    parser.add_argument('supplier_id', help='id of the supplier')

    return parser.parse_args()

def load_product_cache(supplier_id):
    product_cache = {}
    products = openerp.ProductSupplierinfo.browse([("name", "=", int(supplier_id))])
    for product in products:
        if product.product_code is not None:
            print("product ref=%s, base_price=%s" % (product.product_code, product.base_price))
            product_cache[product.product_code] = product

def main():
    # Configure arguments parser
    args = parse_args()

    product_cache = load_product_cache(args.supplier_id)

    supplier_prices = openerp.SupplierPriceList.browse([
        ("supplier_id", "=", int(args.supplier_id)),
        ("apply_date", ">", "2022-01-01"),
        ("apply_date", "<", "2022-11-21")])

    for update in supplier_prices:
        print("New price: product=%s, price=%s, apply=%s" % (update.product_name, update.price, update.apply_date))

if __name__ == "__main__":
    main()
