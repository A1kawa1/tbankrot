import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
from typing import List


class ObjectCard:
    def __init__(self, inn=None, href=None, revenue=None) -> None:
        self.inn = inn
        self.href = href
        self.revenue = revenue


timeout = 10
url = 'https://bo.nalog.ru/search?query={inn}&page=1'

inn_set = []
with open('first.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        if row[5] != '':
            inn_set.append(row[5])

inn_set = set(inn_set)
print('------------------------')
print(inn_set)
print('------------------------')
print(len(inn_set))
print('------------------------')

options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0')
options.add_argument("--start-maximized")
driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)

try:
    driver.get(url.format(inn=list(inn_set)[0]))
    webdriver.common.action_chains.ActionChains(driver).move_by_offset(100, 100).click().perform()
    with open("second.csv", mode='w', encoding='utf-8') as w_file:
        names = list(ObjectCard().__dict__.keys())
        file_writer = csv.DictWriter(w_file, delimiter = ",",
                                     lineterminator="\r",
                                     fieldnames=names)
        file_writer.writeheader()
        for inn in inn_set:
            print(inn, end=' ')
            driver.get(url.format(inn=inn))
            print('-----ПЕРЕШЛИ------', end=' ')
            all_card = driver.find_elements(By.CLASS_NAME, 'results-search-tbody')
            print('-----НАШЛИ КАРТОЧКИ------', end=' ')
            if not len(all_card):
                print(inn, None)
                continue
            

            card = all_card[0]
            print('-----НАШЛИ ПЕРВУЮ КАРТОЧКИ------', end=' ')
            href = card.find_element(By.CLASS_NAME, 'results-search-table-row').get_attribute('href')
            print(href)

            object_card = ObjectCard(inn=inn, href=href)

            driver.get(href)

            '''
            
            тут считать данные с первой страницы
            
            '''
            revenue = 0
            info_box = None
            start_time = time.time()
            while info_box is None:
                try:
                    info_box = driver.find_element(By.ID, 'financialResult')
                    table = info_box.find_elements(By.TAG_NAME, 'table')[0]
                    tr = table.find_elements(By.TAG_NAME, 'tr')[0]
                    year_revenue = float((tr.find_elements(By.TAG_NAME, 'td')[1]
                                            .find_element(By.TAG_NAME, 'span').text).strip().replace(',', '.'))
                    revenue += year_revenue
                    print(year_revenue)
                except:
                    if time.time() - start_time > timeout:
                        break
                    continue

            
            all_year = None
            while all_year is None:
                try:
                    all_year = driver.find_element(By.CLASS_NAME, 'grid-reports-header-top__period').find_elements(By.TAG_NAME, 'button')
                except:
                    continue

            if len(all_year) > 5:
                count_year = 4
                plus_index = -5
            else:
                count_year = len(all_year) - 1
                plus_index = 0

            for k in range(count_year):
                print('-----------CLICK-------------')
                year = None
                while year is None:
                    try:
                        year = driver.find_element(By.CLASS_NAME, 'grid-reports-header-top__period').find_elements(By.TAG_NAME, 'button')[plus_index+k]
                    except:
                        continue
                print(year.text)
                year.click()

                '''
                
                тут считать данные
                
                '''
                info_box = None
                start_time = time.time()
                while info_box is None:
                    try:
                        info_box = driver.find_element(By.ID, 'financialResult')
                        table = info_box.find_elements(By.TAG_NAME, 'table')[0]
                        tr = table.find_elements(By.TAG_NAME, 'tr')[0]
                        year_revenue = float((tr.find_elements(By.TAG_NAME, 'td')[1]
                                                .find_element(By.TAG_NAME, 'span').text).strip().replace(',', '.'))
                        revenue += year_revenue
                        print(year_revenue)
                    except:
                        if time.time() - start_time > timeout:
                            break
                        continue

            revenue = round(revenue, 3)
            object_card.revenue = revenue
            file_writer.writerow(object_card.__dict__)
            print(f'result revenue = {revenue}')
            print('------------------------')

except Exception as ex:
    print(ex)
    time.sleep(100)
finally:
    driver.close()
    driver.quit()
