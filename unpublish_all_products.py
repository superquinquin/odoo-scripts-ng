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
        import odoo_configuration_user_test as odoo_configuration_user

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
products = openerp.ProductProduct.browse([
    ("active", "=", True),
    ("website_published", "=", True)
    ])
for product in products:
    print(product)
    product.website_published = False

