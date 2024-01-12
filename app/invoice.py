import json
import csv

from app.models.expense import ExpenseItem


class ParseInvoice:
    dst_csv = '/Users/sml/git/smltax/dst/invoice.csv'
    src_json = '/Users/sml/git/smltax/data/invoice.json'

    def __init__(self):
        pass

    def run(self):
        with open(self.src_json) as f:
            data = json.load(f)

        rows = []
        for datum in data:

            for item in datum.get('Items', []):
                obj = {}
                obj['product_name'] = item.get('Description')
                obj['product_code'] = item.get('ProductCode')
                obj['quantity'] = item.get('Quantity')

                obj['amount_amount'] = item.get('Amount', {}).get('amount')
                obj['amount_currency_symbol'] = item.get('Amount', {}).get('currencySymbol')
                obj['amount_currency_code'] = item.get('Amount', {}).get('currencyCode')

                obj['unit_price_amount'] = item.get('UnitPrice', {}).get('amount')
                obj['unit_price_currency_symbol'] = item.get('UnitPrice', {}).get('currencySymbol')
                obj['unit_price_currency_code'] = item.get('UnitPrice', {}).get('currencyCode')

                obj['subtotal'] = item.get('Subtotal')
                obj['subtotal_amount'] = item.get('Subtotal', {}).get('amount')
                obj['subtotal_currency_symbol'] = item.get('Subtotal', {}).get('currencySymbol')
                obj['subtotal_currency_code'] = item.get('Subtotal', {}).get('currencyCode')

                obj['vendor_name'] = item.get('VendorName')
                obj['vendor_tax_id'] = item.get('VendorTaxID')
                obj['created_at'] = item.get('created_at')

                obj['payment_term'] = item.get('PaymentTerm')

                row = ExpenseItem.parse_obj(obj)
                rows.append(row)

        with open(self.dst_csv, 'w') as f:
            writer = csv.DictWriter(f, ExpenseItem.__fields__.keys())
            writer.writeheader()
            for row in rows:
                writer.writerow(row.dict())


def main():
    job = ParseInvoice()
    job.run()


if __name__ == '__main__':
    main()
