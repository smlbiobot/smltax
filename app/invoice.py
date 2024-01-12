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

            for idx, item in enumerate(datum.get('Items', [])):
                obj = {}

                obj['invoice_date'] = datum.get('InvoiceDate')
                obj['invoice_id'] = datum.get('InvoiceID')

                obj['invoice_total_amount'] = datum.get('InvoiceTotal', {}).get('amount')
                obj['invoice_total_currency_symbol'] = datum.get('InvoiceTotal', {}).get('currencySymbol')
                obj['invoice_total_currency_code'] = datum.get('InvoiceTotal', {}).get('currencyCode')

                obj['customer_name'] = datum.get('CustomerName')
                obj['customer_address_receipient'] = datum.get('CustomerAddressRecipient')

                obj['product_name'] = item.get('Description')
                obj['product_code'] = item.get('ProductCode')
                obj['quantity'] = item.get('Quantity')

                obj['amount_amount'] = item.get('Amount', {}).get('amount')
                obj['amount_currency_symbol'] = item.get('Amount', {}).get('currencySymbol')
                obj['amount_currency_code'] = item.get('Amount', {}).get('currencyCode')

                obj['unit_price_amount'] = item.get('UnitPrice', {}).get('amount')
                obj['unit_price_currency_symbol'] = item.get('UnitPrice', {}).get('currencySymbol')
                obj['unit_price_currency_code'] = item.get('UnitPrice', {}).get('currencyCode')

                obj['subtotal'] = datum.get('Subtotal')
                obj['subtotal_amount'] = datum.get('Subtotal', {}).get('amount')
                obj['subtotal_currency_symbol'] = datum.get('Subtotal', {}).get('currencySymbol')
                obj['subtotal_currency_code'] = datum.get('Subtotal', {}).get('currencyCode')

                obj['vendor_name'] = datum.get('VendorName')
                obj['vendor_tax_id'] = datum.get('VendorTaxID')
                obj['created_at'] = datum.get('created_at')

                obj['payment_term'] = datum.get('PaymentTerm')

                row = ExpenseItem.parse_obj(obj)

                # skip non rows
                if not row.amount_amount:
                    continue

                if row.amount_amount < 0:
                    continue

                if row.product_name == 'New Relic One - Data (PAYG)' and idx > 0:
                    continue

                if row.vendor_name.startswith('CLOUDFLARE'):
                    if idx > 0:
                        continue

                    if row.product_name.startswith('Card ending with'):
                        continue

                    if row.product_name.startswith('Previous Balance'):
                        continue

                rows.append(row)


        def sort_order(x):
            return (
                x.vendor_name or "",
                x.invoice_date or "",
            )

        rows = sorted(rows, key=sort_order)

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