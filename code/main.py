from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
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


try:
    driver.get('https://tbankrot.ru/login')
    mail = driver.find_element(By.NAME, 'mail')
    mail.send_keys('al.max.bel@mail.ru')
    pas = driver.find_element(By.NAME, 'pas')
    pas.send_keys('Maxpass5')
    pas.send_keys(Keys.ENTER)
    time.sleep(0.5)
    # login = driver.find_element(By.CLASS_NAME, 'submit-btn').click()
    driver.get(url_data.format(page=1))

    select = Select(driver.find_element(By.ID, 'pageItemCol'))
    select.select_by_visible_text('100')
    time.sleep(0.5)
    
    paginator = driver.find_element(By.ID, 'paginator_1').find_elements(By.TAG_NAME, 'li')
    amount_page = int(paginator[-1].text)
    print('---------------')
    print(amount_page)
    print('---------------')
    
    with open("data_tmp.csv", mode="w", encoding='utf-8') as w_file:
        names = ['number', 'lot', 'href', 'start_price']
        file_writer = csv.DictWriter(w_file, delimiter = ",",
                                     lineterminator="\r",
                                     fieldnames=names)
        file_writer.writeheader()
        for page in range(amount_page):

            print('---------------')
            page += 1
            print(page)
        
            driver.get(url_data.format(page=page))

            torg = driver.find_elements(By.CLASS_NAME, 'torg')
            torg_lot = driver.find_elements(By.CLASS_NAME, 'torg lot')
            result = torg + torg_lot

            for el in result:
                main_info = el.find_element(By.CLASS_NAME, 'main_info')
                info_head = main_info.find_element(By.CLASS_NAME, 'info_head')
                price_info = main_info.find_element(By.CLASS_NAME, 'price_info')


                number_lot = info_head.find_element(By.CLASS_NAME, 'num')
                number_href = number_lot.find_element(By.TAG_NAME, 'a')
                number = number_href.text
                print(number, end=' ')
                href = number_href.get_attribute('href')
                print(href, end=' ')
                try:
                    lot = number_lot.find_element(By.TAG_NAME, 'span').text
                    print(lot, end=' ')
                except Exception as e:
                    lot = None
                    print(e, end=' ')

                try:
                    start_price = get_text_excluding_children(
                                    driver,
                                    price_info.find_element(By.CLASS_NAME, 'sum')
                                ).strip()
                    start_price = start_price.replace(',', '.')
                    start_price = float(start_price.replace(' ', ''))
                    print(start_price)
                except Exception as e:
                    start_price = None
                    print(e)
                # deposit = (price_info.find_element(By.CLASS_NAME, 'cur_price')
                #            .find_elements(By.TAG_NAME, 'div')[1]
                #            .find_elements(By.TAG_NAME, 'p')[1].text)

                result_data.append(Lot(
                    number=number,
                    lot=lot,
                    href=href,
                    start_price=start_price
                ))
                file_writer.writerow({
                    'number': number,
                    'lot': lot,
                    'href': href,
                    'start_price': start_price
                })
            print('---------------')

    # with open("data.csv", mode="w", encoding='utf-8') as w_file:
    #     names = list(Lot().__dict__.keys())
    #     file_writer = csv.DictWriter(w_file, delimiter = ",",
    #                                  lineterminator="\r",
    #                                  fieldnames=names)
    #     file_writer.writeheader()
    #     for el in result_data:
    #         print('---------------')
    #         print(el.href)
    #         try:
    #             driver.get(el.href)
    #             debtor = driver.find_elements(By.CLASS_NAME, 'trade_block')[0]
    #             debtor_name = get_text_excluding_children(
    #                 driver,
    #                 debtor.find_element(By.CLASS_NAME, 'head')
    #             ).strip()
    #             el.debtor_name = debtor_name

    #             body = (debtor.find_element(By.CLASS_NAME, 'body')
    #                         .find_elements(By.CLASS_NAME, 'row'))
    #             for el_inn in body:
    #                 text = el_inn.find_elements(By.TAG_NAME, 'div')[0].text
    #                 value = el_inn.find_elements(By.TAG_NAME, 'div')[1].text
    #                 if text == 'ИНН:':
    #                     el.debtor_inn = int(value)
    #                 if text == 'ОГРН:':
    #                     el.debtor_orgn = int(value)

    #             print(el.debtor_name, el.debtor_inn, el.debtor_orgn)
    #         except:
    #             print('ERRRRRRROR')
    #         file_writer.writerow(el.__dict__)
            

    time.sleep(100)

except Exception as ex:
    print(ex)
    time.sleep(100)
finally:
    driver.close()
    driver.quit()