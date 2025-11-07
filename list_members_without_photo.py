#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

import erppeek
import argparse
import csv
import sys

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


openerp, uid, tz = init_openerp(
    odoo_configuration_user["url"],
    odoo_configuration_user["login"],
    odoo_configuration_user["password"],
    odoo_configuration_user["database"],
)


###############################################################################
# Configuration
###############################################################################

###############################################################################
# Script
###############################################################################

avatars = [
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAABDKElEQVR4nO29V7MlV3Iulplrldvm+NMejQYwBsQYKkheXZIRUugq",
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAABAyklEQVR4nO2917Isx7EluNwjUpTY6ggABEABkn2v8fK2mLHph/6L",
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAYAAAA9zQYyAAAD7GlDQ1BpY2MAAHjajZTPbxRlGMc/u/POrAk4B1MBi8GJP4CQQrZg",
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAABCFElEQVR4nO29V7MkR7Im9rlHqhJHdTdaAA05AjO4d65dXrG2JI3G",
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAABBR0lEQVR4nO29WZMt13Um9q21dw5nqKo7AiBAgpMkDhLl7rZaVjva",
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAABDHklEQVR4nO296bNk1ZEn6O7n3CW2t+TLPRNISEAIAVKpSlUqVVdZ",
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAABBv0lEQVR4nO292ZYkx5E2ZmbuHktutXT1hm5s5JCcmX/mSnoQPYYe",
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAAA+PElEQVR4nO29WZMkx9Etdo5HZGZVdfdsIEh+FGW6ZjI96F/q591H",
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAABCZElEQVR4nO2917Ikx9Em6O4RKUod3bohGqD4qWZmd2cv5i3mkfbN",
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAABCDklEQVR4nO29WZMkyZEm9qmauXscedbV1d2FvnANMDsjw5mdlSEp",
    "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAIAAACyr5FlAAA/Q0lEQVR4nO292ZYkR5IldkVU1czcPZbMBBKFqq6u6TmH5AO/kp/E",
]


def is_avatar(b64: str):
    key = b64[:100]
    if key in avatars:
        return True
    return False


def load_member_list_from_csv(filename: str):
    members = []
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            members.append(int(row[0]))
    return members


def parse_args():
    parser = argparse.ArgumentParser(
        description="List all members without a photo"
    )
    # parser.add_argument("var", help="desc")

    return parser.parse_args()


def main():
    # Configure arguments parser
    args = parse_args()

    recent_buyers = load_member_list_from_csv(
        "./query_result_2024-05-11T16_39_27.406715Z.csv"
    )

    print("numero;nom;email")
    for member in openerp.ResPartner.browse(
        [
            ("active", "=", True),
            "|",
            ("is_worker_member", "=", True),
            ("is_associated_people", "=", True),
        ]
    ):
        # if isinstance(member.image, str) and len(member.image) == 0:
        #     print(f"name={member.name} len={len(member.image)}")
        # if (not isinstance(member.image, str)) or len(member.image) < 25000:
        #     print(f"{member.barcode_base};{member.name};{member.email}")
        if isinstance(member.image, str) and not is_avatar(member.image):
            pass
        elif member.id in recent_buyers:
            print(f"{member.barcode_base};{member.name};{member.email}")


if __name__ == "__main__":
    main()
