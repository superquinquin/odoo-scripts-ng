#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta


import erppeek
from openpyxl import load_workbook, Workbook

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


openerp, uid, tz = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])


###############################################################################
# Script
###############################################################################

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_NOTIME_FORMAT = '%d-%m-%Y'


def adress(partnerid):
    cooperateur = []
    partners = openerp.ResPartner.browse([
        ("id", "=", partnerid)])
    for partner in partners:
        (nom, prenom) = partner.name.split(',')
        coop = {
            'id': partner.id,
            'nom': nom.strip(),
            'prenom': prenom.strip(),
            'mail': partner.email,
            'address': "%s %s %s " % (partner.street, partner.zip, partner.city),
        }
        cooperateur.append(coop)
    return cooperateur

# Détermine si le coop n'a pas d'adresse 
def adresse_vide(partnerid):
    adress_vide = False
    partners = openerp.ResPartner.browse([
        ("id", "=", partnerid)])
    for partner in partners:
        if partner.street == "" and partner.zip == "" and partner.city == "":
            return True 
    return adress_vide
    

def afficher_coops(coops):
    for coop in coops:
        # pas d'adresse pour ce coop 
        if (adresse_vide(coop) == True):
            cooperateur = adress(coop)
            print("Sauf erreur, %s %s (%s) n'a pas d'adresse renseignée " %
                  (cooperateur[0]["prenom"], cooperateur[0]["nom"], coop))



# On regarde 2 mois en arrière
currentTimeDate = datetime.now() - relativedelta(months=2)
currentTime = currentTimeDate.strftime('%Y-%m-%d')


#    ("create_date", ">", currentTime),
#    ("partner_id", "like", 'MONNIER')],

# Liste des personnes qui ont achetées dans les 2 derniers mois 
membre_acheteur = []
posOrder = openerp.PosOrder.browse([
    ("create_date", ">", currentTime)],
    order="create_date asc")
for order in posOrder:
    if order.partner_id.id not in membre_acheteur:
        membre_acheteur.append(order.partner_id.id)

afficher_coops(membre_acheteur)
