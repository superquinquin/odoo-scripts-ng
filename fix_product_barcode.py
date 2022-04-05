#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import datetime
import time
import erppeek
import csv
import re

from datetime import date

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
nb_error = 0
products = openerp.ProductProduct.browse([("active", "=", True)])
for product in products:
    if type(product.barcode) is str and len(product.barcode) > 13:
        print("Broken barcode : %s(%d) [%s]" % (product.name, product.id, product.barcode))
        nb_error += 1
        new_barcode = product.barcode.strip(" \u200B")
        print("%s [%s]" % (product.name, new_barcode))
        try:
            product.barcode = new_barcode
        except Exception as e:
            print("** Fix barcode failed for %s : %s" % (product.name, e))

print("Found %d broken barcodes" % (nb_error))
