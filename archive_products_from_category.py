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
        description="Move archived (inactive) products from a specific category to 'Archives' category"
    )
    parser.add_argument(
        "category",
        help="Name or ID of the product category (automatically detected)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without actually moving"
    )

    return parser.parse_args()


def main():
    # Configure arguments parser
    args = parse_args()

    # Search for the category
    ProductCategory = openerp.model("product.category")

    # Try to detect if category is an ID (integer) or a name (string)
    try:
        category_id = int(args.category)
        # It's an integer, search by ID
        categories = ProductCategory.browse([("id", "=", category_id)])

        if not categories:
            print(f"No category found with ID '{category_id}'")
            return

        category = categories[0]  # type: ignore
    except ValueError:
        # It's not an integer, search by name
        categories = ProductCategory.browse([("name", "ilike", args.category)])

        if not categories:
            print(f"No category found matching '{args.category}'")
            return

        if len(categories) > 1:  # type: ignore
            print(f"Multiple categories found matching '{args.category}':")
            for cat in categories:  # type: ignore
                print(f"  - {cat.name} (ID: {cat.id})")  # type: ignore
            print("\nPlease be more specific or use the category ID.")
            return

        category = categories[0]  # type: ignore
    
    print(f"Category: {category.name} (ID: {category.id})")  # type: ignore
    print("-" * 80)
    
    # Search for INACTIVE products in this category
    Product = openerp.model("product.template")
    domain = [
        ("categ_id", "=", category.id),  # type: ignore
        ("active", "=", False)
    ]
    
    archived_products = Product.browse(domain)
    
    if not archived_products:
        print(f"No archived products found in category '{category.name}'")  # type: ignore
        return
    
    print(f"Found {len(archived_products)} archived product(s) to move to 'Archives' category:\n")  # type: ignore

    moved_count = 0
    for product in archived_products:  # type: ignore
        default_code = f"[{product.default_code}]" if product.default_code else ""  # type: ignore
        print(f"  - {product.name} {default_code} (ID: {product.id})")  # type: ignore
        
        if not args.dry_run:
            # Move product to Archives category (ID: 186)
            product.categ_id = 186
            moved_count += 1
    
    print("-" * 80)
    if args.dry_run:
        print(f"[DRY RUN] Would move {len(archived_products)} product(s) to 'Archives' category")  # type: ignore
    else:
        print(f"Successfully moved {moved_count} archived product(s) from '{category.name}' to 'Archives' category")  # type: ignore


if __name__ == "__main__":
    main()
