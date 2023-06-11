from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import csv
import time
from typing import List


def get_text_excluding_children(driver, element):
    return driver.execute_script("""
    return jQuery(arguments[0]).contents().filter(function() {
        return this.nodeType == Node.TEXT_NODE;
    }).text();
    """, element)


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


options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0')
driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
# url_data = 'https://tbankrot.ru/?page={page}&swp=any_word&debtor_cat=0&parent_cat=5&sub_cat=31%2C33&sort_order=desc&sort=relevant&show_period=all'
url_data = 'https://tbankrot.ru/?page={page}&swp=any_word&debtor_cat=0&start_p1=10000000&parent_cat=5&sub_cat=33&sort_order=desc&sort=relevant&show_period=all'

result_data: List[Lot] = []
last = 1101
'''
al.max.bel@mail.ru
al.max.bel@gmail.com
al.maxx.bel@mail.ru
al.maxxx.bel@mail.ru
al.maxxxx.bel@mail.ru
al.maxxxxx.bel@mail.ru
al.maxxxxxx.bel@mail.ru
al.maxxxxxxx.bel@mail.ru
'''

try:
    driver.get('https://tbankrot.ru/login')
    mail = driver.find_element(By.NAME, 'mail')
    mail.send_keys('al.maxxxxxxx.bel@mail.ru')
    pas = driver.find_element(By.NAME, 'pas')
    pas.send_keys('Maxpass5')
    pas.send_keys(Keys.ENTER)
    time.sleep(0.5)


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

    with open("first.csv", mode='a', encoding='utf-8') as w_file:
        names = list(Lot().__dict__.keys())
        file_writer = csv.DictWriter(w_file, delimiter = ",",
                                     lineterminator="\r",
                                     fieldnames=names)
        if last == 1:
            file_writer.writeheader()
        for el in result_data:
            print('---------------')
            print(el.href)
            try:
                driver.get(el.href)
                debtor = driver.find_elements(By.CLASS_NAME, 'trade_block')[0]
                debtor_name = get_text_excluding_children(
                    driver,
                    debtor.find_element(By.CLASS_NAME, 'head')
                ).strip()
                el.debtor_name = debtor_name

                body = (debtor.find_element(By.CLASS_NAME, 'body')
                            .find_elements(By.CLASS_NAME, 'row'))
                for el_inn in body:
                    text = el_inn.find_elements(By.TAG_NAME, 'div')[0].text
                    value = el_inn.find_elements(By.TAG_NAME, 'div')[1].text
                    if text == 'ИНН:':
                        el.debtor_inn = int(value)
                    if text == 'ОГРН:':
                        el.debtor_orgn = int(value)

                print(el.debtor_name, el.debtor_inn, el.debtor_orgn)
            except:
                print('ERRRRRRROR')
            file_writer.writerow(el.__dict__)
            

    time.sleep(100)

except Exception as ex:
    print(ex)
    time.sleep(100)
finally:
    driver.close()
    driver.quit()