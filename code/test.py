from typing import List
import csv

class Lot:
    def __init__(self, number=None, lot=None,
                 href=None, start_price=None,
                 debtor_name=None, debtor_inn=None,
                 debtor_orgn=None) -> None:
        self.number = number
        self.lot = lot
        self.href = href
        self.start_price = start_price
        self.debtor_name = debtor_name
        self.debtor_inn = debtor_inn
        self.debtor_orgn = debtor_orgn


result_data: List[Lot] = []
last = 1

with open('data_tmp.csv', encoding='utf-8') as r_file:
    reader = csv.DictReader(r_file)
    k = 1
    for row in reader:
        if k < last:
            k += 1
            continue
        result_data.append(Lot(
            number=row['number'],
            lot=row['lot'],
            href=row['href'],
            start_price=row['start_price']
        ))

with open("first_cp.csv", mode='a', encoding='utf-8') as w_file:
    names = list(Lot().__dict__.keys())
    file_writer = csv.DictWriter(w_file, delimiter = ",",
                                    lineterminator="\r",
                                    fieldnames=names)
    el = Lot(
        number='12'
    )
    file_writer.writerow(el.__dict__)
