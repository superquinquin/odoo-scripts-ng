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
    parser = argparse.ArgumentParser(
        description="Switch scale group from source to target for all products"
    )
    parser.add_argument(
        "src_group_id",
        type=int,
        help="Source scale group ID"
    )
    parser.add_argument(
        "target_group_id",
        type=int,
        help="Target scale group ID"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which products would be updated without making changes"
    )

    return parser.parse_args()


def main():
    # Configure arguments parser
    args = parse_args()

    src_group_id = args.src_group_id
    target_group_id = args.target_group_id
    dry_run = args.dry_run

    # Get product model
    ProductProduct = openerp.model("product.product")

    # Search for all products with the source scale group
    product_ids = ProductProduct.search([("scale_group_id", "=", src_group_id)])

    print(f"Found {len(product_ids)} products with scale group ID {src_group_id}")

    if not product_ids:
        print("No products to update.")
        return

    if dry_run:
        print("\n[DRY RUN MODE] The following products would be updated:\n")

    # Update each product to use the target scale group
    for product_id in product_ids:
        product = ProductProduct.browse(product_id)
        if dry_run:
            print(f"  - {product.name} (ID: {product_id})")
        else:
            print(f"Updating product {product.name} (ID: {product_id})")
            ProductProduct.write(product_id, {"scale_group_id": target_group_id})

    if dry_run:
        print(f"\n[DRY RUN MODE] {len(product_ids)} products would be updated to scale group ID {target_group_id}")
        print("Run without --dry-run to apply changes.")
    else:
        print(f"\nSuccessfully updated {len(product_ids)} products to scale group ID {target_group_id}")


if __name__ == "__main__":
    main()
