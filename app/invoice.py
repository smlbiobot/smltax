import json
import csv

from app.models.expense import ExpenseItem
import dateparser


class ParseInvoice:
    dst_csv = '/Users/sml/git/smltax/dst/invoice.csv'

    dsv_csvs = [
        '/Users/sml/git/smltax/dst/invoice.csv',
        '/Users/sml/Dropbox/smluniverse/Tax/2022-2023/docs/expenses.csv'
    ]
    src_json = '/Users/sml/git/smltax/data/invoice-out-1705105698274.json'

    src_aws_csv = '/Users/sml/git/smltax/data/aws-fix.csv'
    src_godaddy_csv = '/Users/sml/git/smltax/data/godaddy-export.csv'

    def __init__(self, start_date = '', end_date=''):
        self.start_date = start_date
        self.end_date = end_date

        self.start_date_dt = dateparser.parse(self.start_date, settings={'TIMEZONE': 'UTC'})
        self.end_date_dt = dateparser.parse(self.end_date, settings={'TIMEZONE': 'UTC'})

    def parse_invoice(self):
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

                obj['product_name'] = item.get('Description', "")
                obj['product_code'] = item.get('ProductCode', "")
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

                obj['vendor_name'] = datum.get('VendorName', "")
                obj['vendor_tax_id'] = datum.get('VendorTaxId', "")
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

                if row.vendor_name in ['Akamai', 'Linode']:
                    row.product_name = 'Servers for RoyaleAPI'

                    if idx > 0:
                        continue

                    skip_dates = [
                        '2023-06',
                        '2023-07',
                        '2023-08',
                        '2023-09',
                        '2023-10',
                        '2023-11',
                        '2023-12',
                    ]
                    print(f"{row.invoice_date=}")
                    add_row = True
                    for sd  in skip_dates:
                        if row.invoice_date.startswith(sd):
                            add_row = False

                    if not add_row:
                        continue

                if row.vendor_name in ['Akamai', 'Linode']:
                    row.vendor_name = 'Akamzi / Linode'


                if row.vendor_name.startswith('CLOUDFLARE'):
                    if idx > 0:
                        continue

                    if row.product_name.startswith('Card ending with'):
                        continue

                    if row.product_name.startswith('Previous Balance'):
                        continue

                # 3 HK
                if all([
                    row.invoice_total_currency_code == 'TWD',
                    row.customer_name == 'Mx Lxx Sxx Mxxx',
                ]):
                    row.invoice_total_currency_code = 'HKD'
                    row.product_name = '3HK Mobile Phone Bill'
                    row.vendor_name = '3HK / Supreme'

                # Apple
                if row.product_name.startswith('iCloud'):
                    row.vendor_name = 'Apple'
                    row.invoice_total_currency_code = 'HKD'

                # Midjourney
                if 'Midjourney' in row.vendor_name:
                    if row.product_name.startswith('Rollover'):
                        continue

                if row.invoice_date:
                    row.invoice_date = dateparser.parse(row.invoice_date, settings={'TIMEZONE': 'UTC'}).isoformat()


                rows.append(row)

        return rows

    def parse_aws_rows(self):
        items = []

        with open(self.src_aws_csv) as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:

                if not row.get('Transaction date'):
                    continue

                item = ExpenseItem.parse_obj(dict(
                    invoice_date=dateparser.parse(row['Transaction date']).isoformat(),
                    vendor_name='Amazon Web Services',
                    invoice_id=row['Invoice ID'],
                    producproduct_namet_name="Hosting for RoyaleAPI",
                    payment_term="Payment method",
                    invoice_total_amount=float(row['Amount']),
                    invoice_total_currency_symbol='$',
                    invoice_total_currency_code=row['Currency'],
                    amount_amount=float(row['Amount']),
                    amount_currency_symbol='$',
                    amount_currency_code=row['Currency'],
                    created_at="",
                ))

                items.append(item)
        return items

    def parse_godaddy_rows(self):
        rows = []
        return rows

    def filter_rows(self, rows):
        _rows = []
        for row in rows:
            if not row.invoice_date:
                continue

            row_date = dateparser.parse(row.invoice_date, settings={'TIMEZONE': 'UTC'})

            try:

                if row_date < self.start_date_dt:
                    continue

                if row_date > self.end_date_dt:
                    continue
            except TypeError:
                print(f"{row_date=}")
                print(f"{self.start_date_dt=}")

            _rows.append(row)

        return _rows

    def sort_rows(self, rows):

        def sort_order(x):
            return (
                x.vendor_name or "",
                x.invoice_date or "",
            )

        rows = sorted(rows, key=sort_order)
        return rows

    def calculate_totals(self, rows):
        usd_total = 0
        for row in rows:
            if row.invoice_total_currency_code == 'HKD':
                usd_total += row.invoice_total_amount /7.78
                # pass
            else:
                usd_total += row.invoice_total_amount

        print(f"Total: {usd_total=}")
        print(f"Total: {usd_total/12=}")

    def write_csvs(self, rows):
        ignore_fields = [
            'amount_amount',
            'amount_currency_symbol',
            'amount_currency_code',
        ]

        fields = [f for f in ExpenseItem.__fields__.keys() if f not in ignore_fields]

        for dst_csv in self.dsv_csvs:
            with open(dst_csv, 'w') as f:
                writer = csv.DictWriter(f, fields, extrasaction='ignore')
                writer.writeheader()
                for row in rows:
                    writer.writerow(row.dict())



    def run(self):

        rows = (
                self.parse_invoice() +
                self.parse_aws_rows() +
                self.parse_godaddy_rows()
        )

        # rows = self.filter_rows(rows)
        rows = self.sort_rows(rows)

        self.calculate_totals(rows)
        self.write_csvs(rows)






def main():
    job = ParseInvoice(
        start_date='2022-05-01',
        end_date='2023-05-31',
    )
    job.run()


if __name__ == '__main__':
    main()
