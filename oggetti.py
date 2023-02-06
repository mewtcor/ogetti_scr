#!env/Scripts/python python

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
import time
import csv
import datetime
import logging
from enum import Enum

products = []

# -------------- USER INPUT
un = "customer"
pw = "123456"
headless = 'f'       # t or f | T or F
url = "https://oggetti.com/login/?loggedout=true&wp_lang=en_US"
filename = 'test1'

#----------------------------------------------config---
#-- links
cat_links_xpaths = [
    "//ul[@id='menu-main-menu']/li[position()<4]/a",
    "//h2/a"
]
prod_links_xpaths = [
    "//h3/a"
    ]

#-- product xpaths
product_code_xpath = "//span[@class='sku']"
product_name_xpath = "//h1[@itemprop='name']"
category2_xpath = "//div[@class='breadcrumb']//a[2]"
category1_xapth =""
description_xpath = "//div[@id='tab-description']"
image1_xpath = "//div[@id='image-thumbnail']//div[@class='slick-track']/div[1]//a"
image2_xpath = "//div[@id='image-thumbnail']//div[@class='slick-track']/div[2]//a"
image3_xpath = "//div[@id='image-thumbnail']//div[@class='slick-track']/div[3]//a"
image4_xpath = "//div[@id='image-thumbnail']//div[@class='slick-track']/div[4]//a"
image5_xpath = "//div[@id='image-thumbnail']//div[@class='slick-track']/div[5]//a"
discount_price_xpath = "//div[@class='price']/span"
msrp_xpath = "//div[@class='price']//span[@class='woocommerce-Price-amount amount']"
installation_instruction_xpath = "//a[normalize-space()='Installation Instructions']"
product_detail_label1_xpath = "//table[@class='woocommerce-product-attributes shop_attributes']//tr[1]/th"
variant_description_xpath = "//div[@class='woocommerce-variation-description']"
stock_availability_xpath ="//div[@class='woocommerce-variation-availability'] | //p[@class='stock in-stock']"
dimensions_xpath = "//th[normalize-space()='Dimensions']/following-sibling::td"
finish_color_xpath = "//th[normalize-space()='Finish/Color']/following-sibling::td"
specification_sheet_xpath ="//a[normalize-space()='Specification Sheet']"
supplier_name = "oggetti"
# ---------------------end---

category1 = ""
category2 = ""
category1_urls=[]
category2_urls=[]
product_urls=[]
products = []

def chr_driver(url):
    op = webdriver.ChromeOptions()
    op.add_experimental_option('excludeSwitches', ['enable-logging']) #removes the annoying DevTools listening on ws://127.0.0.1 message in the terminal (windows)
    op.add_argument("window-size=1920x1080")
    op.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
    serv = Service('/home/m3wt/enzo/chromedriver')
    h_mode = input('mode ([h]headless | [f]full): ')
    op.headless = h_mode == 'h'
    if not op.headless:
        if h_mode != 'f':
            logging.warning('check driver headless option')
    logging.debug('Using Selenium WebDriver with Chrome browser')
    browser = webdriver.Chrome(service=serv, options=op)
    logging.debug(f'Scraping initial URL: {url}')
    browser.get(url)
    return browser

def login(un, pw):
    login_btn_sel = "//div[@class='lrm-signin-section is-selected']//button[@type='submit'][normalize-space()='Log in']"
    login_btn = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.XPATH, login_btn_sel))
        )
    user_sel = "//div[@class='lrm-signin-section is-selected']//input[@placeholder='Email or Username']"
    username = driver.find_element(By.XPATH,user_sel)
    # next_btn.click()
    username.clear()
    username.send_keys(un)
    pass_sel = "//div[@class='lrm-signin-section is-selected']//input[@placeholder='Password']"
    password = driver.find_element(By.XPATH, pass_sel)
    password.clear()
    password.send_keys(pw)
    login_btn.click()
    time.sleep(5)
    # blocked here

def extract_cat1():
    global tmp_cat1
    tmp_cat1 = ""
    urls = []
    # category1 / menu
    menu_cat_sel = "//ul[@id='menu-main-menu']/li[position()<4]/a" # category links
    menu_cat_links = driver.find_elements(By.XPATH, menu_cat_sel)
    for cat_link in menu_cat_links:
        link = cat_link.get_attribute('href')
        tmp_cat1 = cat_link.get_attribute("textContent") # optional text extract
        if link not in category1_urls:
            urls.append(link)
    return urls


def extract_cat2():
    urls=[]
    
    # scrape category1 for product links
    for cat_link in category1_urls:
    # for link in category1_urls[:1]:
        logging.debug(f'Scraping catalogue URL: {cat_link}')
        driver.get(cat_link)
        cat_flag_sel = "//h1[@class='text-title-heading']"
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, cat_flag_sel))
        )
        subcat_links_sel = "//h2/a" # product links
        subcat_links = driver.find_elements(By.XPATH,subcat_links_sel)
        
        for i in subcat_links:
            link = i.get_attribute('href')
            if link not in category2_urls:
                urls.append(link)
    return urls

def extract_prod_links():
    urls=[]
    # scrape category2 for product links
    for cat_link in category2_urls:
    # for link in category2_urls[1:2]:
        logging.debug(f'Scraping catalogue URL: {cat_link}')
        driver.get(cat_link)
        time.sleep(8)
        pagination() #display full catalog before extracting links
        prod_links_sel = "//h3/a" # product links
        prod_links = driver.find_elements(By.XPATH,prod_links_sel)
        cat_flag_sel = "//div[@class='woocommerce-result-count hidden-md hidden-sm hidden-xs']"
        WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, cat_flag_sel))
            )
        for i in prod_links:
            link = i.get_attribute('href')
            if link not in product_urls:
                urls.append(link)
    return urls


def parse_prod_links():
    if TEST_SCRAPE:
        for test_url in TEST_URLS:
            logging.debug(f'Scraping product URL: {test_url}')
            driver.get(test_url)
            get_variants()
            
    else:
        for prod_link in product_urls:
            logging.debug(f'Scraping product URL: {prod_link}')
            driver.get(prod_link)
            time.sleep(2)
            get_variants()
            
def get_element_attribute(xpath, attribute):
    try:
        return driver.find_element(By.XPATH, xpath).get_attribute(attribute)
    except NoSuchElementException:
        return ''

product_counter = 0
def extract_data():
    global product_info
    global product_counter

    pcode = get_element_attribute(product_code_xpath, "textContent")
    pname = get_element_attribute(product_name_xpath, "textContent")
    category2 = get_element_attribute(category2_xpath, "textContent")
    image1 = get_element_attribute(image1_xpath, "href")
    description = get_element_attribute(description_xpath, "innerHTML")
    msrp = get_element_attribute(msrp_xpath, "textContent")
    discounted_price = get_element_attribute(discount_price_xpath, "textContent")
    image2 = get_element_attribute(image2_xpath, "href")
    image3 = get_element_attribute(image3_xpath, "href")
    image4 = get_element_attribute(image4_xpath, "href")
    image5 = get_element_attribute(image5_xpath, "href")
    installation_instruction = get_element_attribute(installation_instruction_xpath, "href")
    product_detail_label1 = get_element_attribute(product_detail_label1_xpath, "textContent")
    variant_description = get_element_attribute(variant_description_xpath, "textContent")
    stock_availability = get_element_attribute(stock_availability_xpath, "textContent")
    dimensions = get_element_attribute(dimensions_xpath, "textContent")
    finish_color = get_element_attribute(finish_color_xpath, "textContent")
    specification_sheet = get_element_attribute(specification_sheet_xpath, "href")

    today = datetime.datetime.today()
    scrape_date = today.strftime("%d/%m/%Y")
    supplier = supplier_name
    pageUrl = driver.current_url
    # category1 = tmp_cat1

    product_info = {
        'product_code': pcode,
        'product_name': pname,
        #'category1': category1,
        'category2': category2,
        'image1': image1,
        'image2': image2,
        'image3': image3,
        'image4': image4,
        'image5': image5,
        'description': description,
        'msrp': msrp,
        'discounted_price': discounted_price,
        'installation_instruction': installation_instruction,
        'product_detail_label1': product_detail_label1,
        'variant_description': variant_description,
        'stock_availability':stock_availability,
        'dimensions':dimensions,
        'finish_color': finish_color,
        'specicification_sheet' : specification_sheet,
        'scrape_date': scrape_date,
        'supplier': supplier,
        'pageUrl': pageUrl

    }
    if checkVar == True:
        product_info['variant1'] = tmp_var1
        product_info['variantLabel1'] = tmp_varLabel1
    else:
        product_info['variant1'] = ""
        product_info['variantLabel1'] = ""
        # variants = var_list
        # print(variants)
        # for variant in variants:
        #     # variant[i] = var_list[i]
        #     product_info['variant1'] = variant
        #     product_info['variantLabel1'] = tmp_varLabel1
    product_counter +=1
    logging.debug(f'{product_counter}.Extracted product: {pcode} | {pname}')
    products.append(product_info)
    #call pagination function
    pagination()

def get_variants():
    global checkVar
    global tmp_varLabel1
    global tmp_var1
    global data
    # global product_counter

    # global var_list
    try: # PRODUCTS WITH VARIANTS
        variant_elem = driver.find_element(By.XPATH,"//table[@class='variations']/preceding-sibling::div[not(@data-product_variations='[]')]/following-sibling::table[@class='variations']//tr[1]/td[@class='value']/select | //table[@class='variations']//tr[1]/td[@class='value']/div/@class[not(contains(.,'hidden'))]/parent::div")
        no_stock_sel = "//span[@class='stock']" #check for no stock
        try:
            driver.find_element(By.XPATH,no_stock_sel)
            checkVar = False
            # product_counter +=1 
            data = extract_data()
            return
        except NoSuchElementException:
            checkVar = True
            # var_list = []
            for i in range(len(variant_elem.find_elements(By.XPATH, "./div | .//option[position()>1]"))):
                # tmp_var = {}
                variant_elem.find_elements(By.XPATH, "./div | .//option[position()>1]")[i].click()
                tmp_var1 = variant_elem.find_elements(By.XPATH,"./div/div/following-sibling::span | .//option[position()>1]")[i].text
                # tmp_var[i] = variant_elem.find_elements(By.XPATH, ".//option")[i].text
                # var_list.append(tmp_var[i])
                tmp_varLabel1 = driver.find_element(By.XPATH,"//table[@class='variations']//td[1]//label").get_attribute("textContent")
                # product_counter +=1 
                data = extract_data()
            return  
    except NoSuchElementException: # NO VARIANTS
        checkVar = False
        # product_counter +=1 
        data = extract_data()

def pagination():
    found = False
    while not found:
        
        scroll_to_sel = "//a[normalize-space()='Privacy Policy']"
        scroll_to_elem = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, scroll_to_sel))
            )
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(3)
        # Scroll to the top of the page
        driver.execute_script("window.scrollBy(0, -document.body.scrollHeight);")
        time.sleep(3)
        # Scroll back to the bottom of the page
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(3)
        # Scroll back to the top of the page
        driver.execute_script("window.scrollBy(0, -document.body.scrollHeight);")
        # Scroll back to the bottom of the page
        # driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        # time.sleep(8)

        # loc elem as flag 
        found_flag_scrollable_sel = "//div[@class='woocommerce-result-count hidden-md hidden-sm hidden-xs'][not(contains(.,'all'))]"
        try:
            driver.find_element(By.XPATH,found_flag_scrollable_sel)
            found = False
        except NoSuchElementException:
            found = True
    # testprint = "//div[@class='woocommerce-result-count hidden-md hidden-sm hidden-xs']"
    # print(driver.find_element(By.XPATH,testprint).get_attribute("textContent"))
    # print(driver.current_url)
    # time.sleep(6)


def save(data):
    #save to csv
    with open(f'{filename}.csv', 'w', newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=product_info.keys())
        writer.writeheader()
        writer.writerows(products)
    logging.info(f"Export to CSV file {filename} is finished.")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%d-%m-%Y:%H:%M:%S',
                        level=logging.DEBUG)
    logging.getLogger("selenium").setLevel(logging.INFO)
    # ---- block logs from the urllib3.connectionpool logger
    # Set the root logger's level to debug
    logging.getLogger().setLevel(logging.DEBUG)
    # Get the logger for the `urllib3.connectionpool` module
    connectionpool_logger = logging.getLogger("urllib3.connectionpool")
    # Set the logger's level to warning, which is above debug
    connectionpool_logger.setLevel(logging.WARNING)


    driver = chr_driver(url)
    login(un,pw)

    test1 = "https://oggetti.com/product/remini-cocktail-base-dark/"
    test2 ="https://oggetti.com/product/este-arm-chair/"
    test3 = "https://oggetti.com/product/a-cote-table/"
    test4 = "https://oggetti.com/product/bamboo-tray-grn/"
    test5 = "https://oggetti.com/product/hanako-cocktail-table/"
    TEST_URLS = [test1,test2, test3, test4, test5]
    TEST_SCRAPE = False
    # for url in urls:
    #     driver.get(url)
    #     get_variants()
    
    category1_urls = extract_cat1()
    category2_urls = extract_cat2()
    product_urls = extract_prod_links()
    parse_prod_links()
    # get_variants()
    # print(data)
    save(data)
    driver.quit()

