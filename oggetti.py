from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.chrome.options import Options
# from fake_useragent import UserAgent
# import re
import time
import csv
import datetime


products = []
# -------------- USER INPUT
un = "customer"
pw = "123456"
headless = 'f'       # t or f | T or F
url = "https://oggetti.com/login/?loggedout=true&wp_lang=en_US"
filename = 'test1'
# ---------------------

# fix xpaths
# results_flag_sel = "//span[@class='col-6 text-left']//span[@class='ng-star-inserted']"

category1 = ""
category2 = ""
count = 0
category1_urls=[]
category2_urls=[]
product_urls=[]
products = []

def chr_driver(url):
    op = webdriver.ChromeOptions()
    op.add_argument("window-size=1920x1080")
    op.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
    serv = Service('/home/m3wt/enzo/chromedriver')
    if headless == 't' or headless == 'T':
        op.headless = True
    elif headless == 'f' or headless == 'F':
        op.headless = False
    else:
        print('check driver headless option')
    browser = webdriver.Chrome(service=serv, options=op)
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

    # sub categories

def extract_cat1():
    urls = []
    # category1 / menu
    menu_cat_sel = "//ul[@id='menu-main-menu']/li[1]/a" # category links
    menu_cat_links = driver.find_elements(By.XPATH, menu_cat_sel)
    for cat_link in menu_cat_links:
        link = cat_link.get_attribute('href')
        if link not in category1_urls:
            urls.append(link)
    return urls

def extract_cat2():
    urls=[]
    
    # scrape category1 for product links
    for link in category1_urls:
    # for link in category1_urls[:1]:
        driver.get(link)
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
    
    # scrape category1 for product links
    for link in category2_urls:
    # for link in category2_urls[1:2]:
        driver.get(link)
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
        #runs pagination function
        pagination()
    return urls


def parse_prod_links():
    for link in product_urls:
        driver.get(link)
        image_flag_sel = "//div[@class='zoomWindow']"
        WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, image_flag_sel))
            )
        #----- extract data
        try:
            pcode = driver.find_element(By.XPATH,"//span[@class='sku']").get_attribute("textContent")
        except NoSuchElementException:
            pcode = ''
        try:
            pname = driver.find_element(By.XPATH,"//h1[@itemprop='name']").get_attribute("textContent")
        except NoSuchElementException:
            pname = ''
        try:
            image1 = driver.find_element(By.XPATH,"//div[@id='image-thumbnail']//div[@class='slick-track']/div[1]//a").get_attribute("href")
        except:
            image1 = ''
        try:
            description = driver.find_element(By.XPATH,"//div[@id='tab-description']").get_attribute("innerHTML")
        except NoSuchElementException:
            description = ''
        try:
            msrp = driver.find_element(By.XPATH,"//div[@class='price']//span[@class='woocommerce-Price-amount amount']").get_attribute("textContent")
        except NoSuchElementException:
            msrp = ''
        try:
            image2 = driver.find_element(By.XPATH,"//div[@id='image-thumbnail']//div[@class='slick-track']/div[2]//a").get_attribute("href")
        except:
            image2 = ''
        try:
            image3 = driver.find_element(By.XPATH,"//div[@id='image-thumbnail']//div[@class='slick-track']/div[3]//a").get_attribute("href")
        except:
            image3 = ''
        try:
            image4 = driver.find_element(By.XPATH,"//div[@id='image-thumbnail']//div[@class='slick-track']/div[4]//a").get_attribute("href")
        except:
            image4 = ''        
        try:
            image5 = driver.find_element(By.XPATH,"//div[@id='image-thumbnail']//div[@class='slick-track']/div[5]//a").get_attribute("href")
        except:
            image5 = ''
        try:
            installation_instruction = driver.find_element(By.XPATH,"//a[normalize-space()='Installation Instructions']").get_attribute("href")
        except:
            installation_instruction = ''
        try:
            product_detail_label1 = driver.find_element(By.XPATH,"//table[@class='woocommerce-product-attributes shop_attributes']//tr[1]/th").get_attribute("textContent")
        except NoSuchElementException:
            product_detail_label1 = ''
        today = datetime.datetime.today()
        scrape_date = today.strftime("%d/%m/%Y")
        pageUrl = driver.current_url
        global product_info
        product_info = {
            'product_code': pcode,
            'product_name': pname,
            'image1': image1,
            'image2': image2,
            'image3': image3,
            'image4': image4,
            'image5': image5,
            'description': description,
            'msrp': msrp,
            'installation_instruction': installation_instruction,
            'product_detail_label1': product_detail_label1,
            'scrape_date': scrape_date,
            'pageUrl': pageUrl
        }
        print(f'pcode: {pcode} pname: {pname}')
        products.append(product_info)
        #call pagination function
        pagination()

def pagination():
    found = False
    while not found:
        
        scroll_to_sel = "//a[normalize-space()='Privacy Policy']"
        scroll_to_elem = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, scroll_to_sel))
            )
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(5)
        # Scroll to the top of the page
        driver.execute_script("window.scrollBy(0, -document.body.scrollHeight);")
        time.sleep(5)
        # Scroll back to the bottom of the page
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(5)
        # Scroll back to the top of the page
        driver.execute_script("window.scrollBy(0, -document.body.scrollHeight);")
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
    print('data saved')

if __name__ == '__main__':
    driver = chr_driver(url)
    login(un,pw)
    category1_urls = extract_cat1()
    category2_urls = extract_cat2()
    product_urls = extract_prod_links()
    data = parse_prod_links()
    print(data)
    save(data)
    driver.quit()

