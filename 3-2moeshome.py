#!env/Scripts/python python

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from time import sleep
import csv
import datetime
import logging
import re
import json
import undetected_chromedriver as uc


products = []
tmp_var1 = ""
tmp_var2=""
tmp_varLabel1 = ""
tmp_varLabel2 = ""
tmp_swatch_image1 = ""
tmp_swatch_image2 = ""

# -------------- USER INPUT
# un = "customer"
# pw = "123456"
filename = 'moeshome-full'

test1 = "https://www.moeshome.com/living-room/sofas/rodrigo-sofa-black" # no variant
test2 = "https://www.moeshome.com/benches-stools/lund-stool-black-oak-bc112602" # 1 row variants
test3 = "https://www.moeshome.com/dining-room/dining-tables/malibu-round-dining-table-natural" # 2-row variants
test4 = "https://www.moeshome.com/living-room/sofas/abigail-chaise-orange-me105312" # variant 2 - page not found
test5 = "https://www.moeshome.com/living-room/sectionals/jamara-left-facing-sectional-charcoal-grey-ub101607l" # missing product

TEST_URLS = [test1]
TEST_MODE = True

with open('3-2config.json', 'r') as f:
    config_json = json.load(f)
    #----------------------- links
    initial_url = (config_json['initial_url'])
    initial_page_xpath = (config_json['config_links']['initial_page_xpath']['xpath'])
    cat1_xpath = (config_json['config_links']['category1']['xpath'])
    prod_links_xpath = (config_json['config_links']['products']['xpath'])
    next_page_xpath = (config_json['config_links']['next_page']['xpath'])
    variants_flag_xpath = (config_json['config_others']['variants_flag']['xpath'])
    variants_xpath = (config_json['config_others']['variants']['xpath'])
    # ---------------------- product attributes
    product_code_xpath = (config_json['config_products']['product_code']['xpath'])
    product_name_xpath = (config_json['config_products']['product_name']['xpath'])
    # category1_xpath = 
    description_xpath = (config_json['config_products']['description']['xpath'])
    image1_xpath = (config_json['config_products']['image1']['xpath'])
    images_xpath = (config_json['config_products']['images']['xpath'])
    # ---------------------- custom attributes
    price_xpath = (config_json['custom_attributes']['price'])
    color_xpath = (config_json['custom_attributes']['color'])
    product_materials_xpath = (config_json['custom_attributes']['product_materials'])
    arm_height_xpath = (config_json['custom_attributes']['arm_height'])
    seat_height_xpath = (config_json['custom_attributes']['seat_height'])
    style_xpath = (config_json['custom_attributes']['style'])
    general_dimensions_xpath = (config_json['custom_attributes']['general_dimensions'])
    arm_width_xpath = (config_json['custom_attributes']['arm_width'])
    arm_depth_xpath = (config_json['custom_attributes']['arm_depth'])
    seat_width_xpath = (config_json['custom_attributes']['seat_width'])
    seat_depth_xpath = (config_json['custom_attributes']['seat_depth'])
    seating_xpath = (config_json['custom_attributes']['seating'])
    country_of_origin_xpath = (config_json['custom_attributes']['country_of_origin'])
    assembly_intructions_xpath = (config_json['custom_attributes']['assembly_instructions'])
    bed_size_xpath = (config_json['custom_attributes']['bed_size'])
    shape_xpath = (config_json['custom_attributes']['shape'])
    orientation_xpath = (config_json['custom_attributes']['orientation'])
    leg_height_xpath = (config_json['custom_attributes']['leg_height'])
    supplier_name = (config_json['custom_attributes']['supplier_name'])
    variant1_xpath = (config_json['custom_attributes']['variant1'])
    variant2_xpath = (config_json['custom_attributes']['variant2'])
    variant_label1_xpath = (config_json['custom_attributes']['variant_label1'])
    variant_label2_xpath = (config_json['custom_attributes']['variant_label2'])
    swatch_image1_xpath = (config_json['custom_attributes']['swatch_image1'])
    swatch_image2_xpath = (config_json['custom_attributes']['swatch_image2'])
    # ----------- others
    cookie_xpath =(config_json['config_others']['cookie']['xpath'])
    view_all_xpath = (config_json['config_others']['view_all']['xpath'])

category1_urls = []
category2_urls = []
product_urls = []
products = []

def chr_driver():
    op = webdriver.ChromeOptions()
    op.add_experimental_option('excludeSwitches', ['enable-logging']) #removes the annoying DevTools listening on ws://127.0.0.1 message in the terminal (windows)
    # op.add_argument("window-size=1920x1080")
    op.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36")
    # op.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # disable images
    serv = Service(r'C:\Users\mewtc\work\vesta\chromedriver')
    h_mode = input('mode ([h]headless | [f]full): ')
    op.headless = h_mode == 'h'
    if not op.headless:
        if h_mode != 'f':
            logging.warning('check driver headless option')

    logging.debug('Using Selenium WebDriver with Chrome browser')
    browser = webdriver.Chrome(service=serv, options=op)
    return browser

# def chr_driver():
#     op = uc.ChromeOptions()
#     op.add_argument("--disable-blink-features")
#     op.add_argument("--disable-blink-features=AutomationControlled")
#     op.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36")
#     op.add_argument("--no-sandbox")
#     op.add_argument("--disable-extensions")
#     op.add_argument("--dns-prefetch-disable")
#     op.add_argument("--disable-gpu")
#     op.add_argument("--start-maximized")

#     serv = Service(r'C:\Users\mewtc\work\vesta\chromedriver')
#     h_mode = input('mode ([h]headless | [f]full): ')
#     op.headless = h_mode == 'h'
#     if not op.headless:
#         if h_mode != 'f':
#             logging.warning('check driver headless option')

#     logging.debug('Using Selenium WebDriver with Chrome browser')
#     browser = uc.Chrome(service=serv, options=op)

#     return browser


def scrape_initial_page():
    tmp_cat1 = ""
    urls = set()

    # menu
    menu_cat_links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, initial_page_xpath))
    )
    # menu_cat_links = driver.find_elements(By.XPATH, initial_page_xpath)
    for link in menu_cat_links:
        url = link.get_attribute('href')
        child_elem = link.find_element(By.XPATH, "./div")
        tmp_cat1 = child_elem.get_attribute("textContent") # optional text extract
        if url not in category1_urls:
            # urls.append((link,tmp_cat1))
            urls.add((url, tmp_cat1))
    return list(urls)


def click_view_all(): # OPTIONAL
    try:
        view_all_elem = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, view_all_xpath))
        )
        view_all_elem.click()
    except:
        pass

def get_category_links():
    for url in category1_urls:
        logging.debug(f'Scraping category URL: {url[0]} | cat1: {url[1]}')
        driver.get(url[0])
        # sleep(3)
        tmp_cat1 = url[1]
        sleep(1.5)
        click_view_all()
        get_cat1_urls(cat1_xpath, tmp_cat1)


def get_cat1_urls(xpath, cat1):
    tmp_cat2 = ""
    count = 0
    # urls=set()
    cat_links = driver.find_elements(By.XPATH, xpath)
    for link in cat_links:
        url = link.get_attribute('href')
        tmp_cat1 = cat1
        tmp_cat2 = link.get_attribute("textContent")
        if url not in category2_urls:
            # urls.add((url, tmp_cat1, tmp_cat2))
            category2_urls.append((url, tmp_cat1, tmp_cat2))
            count += 1
    print(f'Added {count} urls in the category links queue.')

def get_prod_links():
    for link in category2_urls:
    # for link in category2_urls[1:2]:
        logging.debug(f'Scraping catalogue URL: {link[0]} | cat1: {link[1]} | cat2: {link[2]}')
        driver.get(link[0])
        sleep(1)
        tmp_cat1 = link[1]
        tmp_cat2 = link[2]
        sleep(3)
        # pagination() #OPTIONAL INFINITE PAGINATION
        get_prod_urls(prod_links_xpath, tmp_cat1, tmp_cat2)
        pagination(tmp_cat1, tmp_cat2)


def get_prod_urls(xpath, cat1, cat2):
    urls = set()
    keepscrolling = True
    while keepscrolling == True:
        try:
            prod_links = driver.find_elements(By.XPATH,xpath)
            count = 0
            for link in prod_links:
                url = link.get_attribute('href')
                if url not in urls:
                    urls.add((url, cat1, cat2))
                set2list = list(urls)
                for i in set2list:
                    if i not in product_urls:
                        count += 1
                        product_urls.append(i)
            print(f'Added {count} urls in the product links queue.')
            if count == 0:
                keepscrolling = False
            # Scroll the last element into view using JavaScript
            last_elem = prod_links[-1]
            driver.execute_script("arguments[0].scrollIntoView();", last_elem)
            sleep(5)
            # #  // FLAG scraper to stop scrolling
            # try:
            #     driver.find_element(By.XPATH, last_elem) #end of the product list in the current page
            #     keepscrolling = False
            #     # pagination() #check for pagination
            # except:
            #     print('no such element')
            #     continue
        except:
            break
            # pagination(
   
def pagination(cat1, cat2):
    next_page_x = next_page_xpath
    while True:
        try:
            # Check whether nextPage_xpath exists
            nextPage_elem = driver.find_element(By.XPATH, next_page_x)
            next_page = nextPage_elem.get_attribute("href")
            # If nextPage_xpath exists, call the get_cat_urls function and update nextPage_xpath
            driver.get(next_page)
            sleep(2)
            get_prod_urls(prod_links_xpath, cat1, cat2)
        except NoSuchElementException:
            # If nextPage_xpath does not exist, break out of the loop
            break


def scrape_prod_links():
    global checkVar
    if TEST_MODE is True:
        for test_url in TEST_URLS:
            logging.debug(f'Scraping TEST URL: {test_url}')
            driver.get(test_url)
            allowCookie()
            # driver.maximize_window()
            # sleep(15)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, image1_xpath))
            )
            sleep(3)
            if variantsCheck() is True:
                get_variants('test', 'test')
            else:
                extract_data('test', 'test')          
    else:
        for link in product_urls:
            logging.debug(f'Scraping product URL: {link[0]} | category1: {link[1]} | category2: {link[2]}')
            driver.get(link[0])
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, image1_xpath))
            # )
            tmp_cat1 = link[1]
            tmp_cat2 = link[2]
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, image1_xpath))
            )
            sleep(3)
            if variantsCheck() is True:
                get_variants(tmp_cat1, tmp_cat2)
            else:
                extract_data(tmp_cat1, tmp_cat2)

def viewMoreSpecs():
    try:
        viewmorespecs_xpath = "//p[normalize-space()='View more specifications']"
        view_more_specs_elem = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, viewmorespecs_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView();", view_more_specs_elem)
        view_more_specs_elem.click()
        # sleep(0.5)
        driver.execute_script("window.scrollTo(0, 0)")
    except:
        pass # print('Unable to find view more specs xpath')

def variantsCheck():
    if not variants_flag_xpath:
        istherevariants = False
        # print("Variants flag XPath is empty or null.")
    else:
        elements = driver.find_elements(By.XPATH, variants_flag_xpath)
        if elements:
            istherevariants = True
            # print("Variants flag found.")
        else:
            istherevariants = False
            # print("Variants flag not found.")
    # print("Is there variants?", istherevariants)
    return istherevariants


def get_element_attribute(xpath, attribute):
    try:
        return driver.find_element(By.XPATH, xpath).get_attribute(attribute)
    except NoSuchElementException:
        return ''

def getImages():
    images=[]
    thumbnails_elem = driver.find_elements(By.XPATH, images_xpath)
    # thumbnails_elem = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, images_xpath))
    #         )

    for i in thumbnails_elem:
        # driver.execute_script("arguments[0].click();", i)
        # i.click() # CLICKS THUMBNAILS
        # sleep(2)
        # active_image_elem = driver.find_element(By.XPATH, image1_xpath)
        url = i.get_attribute("srcset")
        if url not in images:
            pattern = r"^(.*?)(?:\s1x,)"
            match = re.search(pattern, url)
            if match:
                images.append(match.group(1))
    return images
product_counter = 0

def extract_data(cat1, cat2):
    # viewMoreSpecs() # view more specs
    global product_info
    global product_counter
    # if checkVar == True:
    #     pcode = get_element_attribute(product_code_xpath, "textContent") + " - " +  tmp_var1
    # else:
    #     pcode = get_element_attribute(product_code_xpath, "textContent")
    pcode = get_element_attribute(product_code_xpath, "textContent").strip()
    if pcode not in [product['product_code'] for product in products]:
        pname = get_element_attribute(product_name_xpath, "textContent")
        # category1 = get_element_attribute(product_category1_xpath, "textContent")
        # category2 = get_element_attribute(product_category2_xpath, "textContent")
        category1 = cat1
        category2 = cat2
        getImages()
        # image1_srcset = get_element_attribute(image1_xpath, "srcset")
        description = get_element_attribute(description_xpath, "innerHTML")

        #variants
        variant1 = get_element_attribute(variant1_xpath, "textContent")
        variant2 = get_element_attribute(variant2_xpath, "textContent")
        variant_label1 = get_element_attribute(variant_label1_xpath, "textContent")
        variant_label2 = get_element_attribute(variant_label2_xpath, "textContent")
        swatch_image1 = get_element_attribute(swatch_image1_xpath, "src")
        swatch_image2 = get_element_attribute(swatch_image2_xpath, "src")

        price = get_element_attribute(price_xpath, "textContent")
        color = get_element_attribute(color_xpath, "textContent")
        product_materials = get_element_attribute(product_materials_xpath, "textContent")
        arm_height = get_element_attribute(arm_height_xpath, "textContent")
        seat_height = get_element_attribute(seat_height_xpath, "textContent")
        style = get_element_attribute(style_xpath, "textContent")
        general_dimensions = get_element_attribute(general_dimensions_xpath, "textContent")
        arm_width = get_element_attribute(arm_width_xpath, "textContent")
        arm_depth = get_element_attribute(arm_depth_xpath, "textContent")
        seat_width = get_element_attribute(seat_width_xpath, "textContent")
        seat_depth = get_element_attribute(seat_depth_xpath, "textContent")
        seating = get_element_attribute(seating_xpath, "textContent")
        country_of_origin = get_element_attribute(country_of_origin_xpath, "textContent")
        assembly_intructions = get_element_attribute(assembly_intructions_xpath, "href")
        bed_size = get_element_attribute(bed_size_xpath, "textContent")
        shape = get_element_attribute(shape_xpath, "textContent")
        orientation = get_element_attribute(orientation_xpath, "textContent")
        leg_height = get_element_attribute(leg_height_xpath, "textContent")
        today = datetime.datetime.today()
        scrape_date = today.strftime("%d/%m/%Y")
        supplier = supplier_name
        pageUrl = driver.current_url


        product_info = {
            'product_code': pcode,
            'product_name': pname,
            'category1' : category1,
            'category2': category2,
            'description': description,
            'variant1': variant1,
            'variant2': variant2,
            'variant_label1': variant_label1,
            'variant_label2': variant_label2,
            'swatch_image1': swatch_image1,
            'swatch_image2': swatch_image2,
            # 'image1': image1,
            'price' : price,
            'color' : color,
            'product_materials': product_materials,
            'arm_height': arm_height,
            'seat_height': seat_height,
            'style': style,
            'general_dimensions': general_dimensions,
            'arm_width': arm_width,
            'arm_depth': arm_depth,
            'seat_width': seat_width,
            'seat_depth': seat_depth,
            'seating': seating,
            'country_of_origin': country_of_origin,
            'assembly_instructions': assembly_intructions,
            'bed_size': bed_size,
            'shape': shape,
            'orientation': orientation,
            'leg_height': leg_height,
            'pageUrl': pageUrl,
            'scrape_date': scrape_date,
            'supplier': supplier

        }
        # product_info['variant1'] = tmp_var1
        # product_info['variantLabel1'] = tmp_varLabel1
        # product_info['swatch_image1'] = tmp_swatch_image1
        # product_info['variant2'] = tmp_var2
        # product_info['variantLabel2'] = tmp_varLabel2
        # product_info['swatch_image2'] = tmp_swatch_image2

        # product_info['variant1'] = tmp_var1 if tmp_var1 else ''
        # product_info['variantLabel1'] = tmp_varLabel1 if tmp_varLabel1 else ''
        # product_info['swatch_image1'] = swatch_image1 if swatch_image1 else ''


        # image_lst = getImages()
        # # Define the maximum number of iterations ex. max_iterations = 20 OPTIONAL
        # # Loop through the list of images and assign to corresponding variables
        # for i in range(len(image_lst)):
        #     if i <= len(image_lst):
        #         match = re.search(r'^([^ ]+)', image_lst[i])
        #         if match:
        #             product_info[f'image{i+1}']  = match.group(1)
        #         else:
        #             product_info[f'image{i+1}']  = ""            
        #     else:
        #         product_info[f'image{i+1}'] = ""

        image_lst = getImages()
        # Define the maximum number of iterations
        max_iterations = 15
        # Loop through the list of images and assign to corresponding variables
        for i in range(max_iterations):
            if i < len(image_lst):
                product_info[f'image{i+1}'] = image_lst[i]
            else:
                product_info[f'image{i+1}'] = ""
        product_counter +=1
        logging.debug(f'{product_counter}.Extracted product: {pcode} | {pname}')
        products.append(product_info)
        #call pagination function
        # pagination()
    else:
        print('Product code already scraped. Skipping...')

# def get_variants(cat1, cat2):
#     global tmp_var1, tmp_var2, tmp_varLabel1, tmp_varLabel2, tmp_swatch_image1, tmp_swatch_image2
#     count_var = 0
#     # global var_list
#     count_var_elem = driver.find_elements(By.XPATH, variants_xpath)
#     count_var = len(count_var_elem)
#     if count_var == 1:
#         var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
#         var_elem1_lst = var_elem1.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")
#         for i in range(0, len(var_elem1_lst)):
#             # scroll to the top of the page
#             driver.execute_script("window.scrollTo(0, 0)")
#             # sleep(1)
#             try: # catch page not found errors
#                 var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
#             except:
#                 break
#             # var_elem1.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")[i].click()
#             try:
#                 var_elem1.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")[i].click()
#             except:
#                 print('disabled element skipping click event')
#                 break
#             sleep(1)
#             viewMoreSpecs()
#             try: #catch PAGE NOT FOUND errors
#                 var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
#             except:
#                 break
#             tmp_var1 = var_elem1.find_element(By.XPATH,"./div[1]/span[2]").get_attribute("textContent")
#             varLabel1_elem = var_elem1.find_element(By.XPATH,"./div[1]/span[1]")
#             tmp_varLabel1 = varLabel1_elem.get_attribute('textContent')
#             try:
#                 tmp_swatch_image1 = var_elem1.find_element(By.XPATH,"./div[2]/div/@class[contains(.,'active')]/parent::div/img").get_attribute('src')

#             except:
#                 tmp_swatch_image1 =""
#             extract_data(cat1, cat2)
#     elif count_var == 2:
#         var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
#         var_elem1_lst = var_elem1.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")
#         for i in range(0, len(var_elem1_lst)):
#             # scroll to the top of the page
#             driver.execute_script("window.scrollTo(0, 0)")
#             # sleep(1)
#             try: #catch page not found errors
#                 var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
#             except:
#                 print('var_elem1 break')
#                 break
#             # var_elem1.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")[i].click()
#             try:
#                 var_elem1.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")[i].click()
#             except:
#                 print('disabled element skipping click event')
#                 break
#             # var_elem1.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")[i].click()
#             sleep(1)
#             viewMoreSpecs()

#             try: #catch page not found errors
#                 var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
#             except:
#                 break
#             tmp_var1 = var_elem1.find_element(By.XPATH,"./div[1]/span[2]").get_attribute("textContent")
#             varLabel1_elem = var_elem1.find_element(By.XPATH,"./div[1]/span[1]")
#             tmp_varLabel1 = varLabel1_elem.get_attribute('textContent')
#             try:
#                 tmp_swatch_image1 = var_elem1.find_element(By.XPATH,"./div[2]/div/@class[contains(.,'active')]/parent::div/img").get_attribute('src')

#             except:
#                 tmp_swatch_image1 =""
#             try: #catch page not found errors
#                 var_elem2 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[2]")
#             except:
#                 break
#             var_elem2_lst = var_elem2.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")
#             for i in range(0, len(var_elem2_lst)):
#                 driver.execute_script("window.scrollTo(0, 0)") # scroll to the top of the page
#                 # sleep(1)
#                 try:
#                     var_elem2.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")[i].click()
#                 except:
#                     print('disabled element skipping click event')
#                     break
#                 sleep(1)
#                 viewMoreSpecs()
#                 try: #catch page not found errors
#                     var_elem2 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[2]")
#                 except:
#                     break
#                 tmp_var2 = var_elem2.find_element(By.XPATH,"./div[1]/span[2]").get_attribute("textContent")
#                 varLabel2_elem = var_elem2.find_element(By.XPATH,"./div[1]/span[1]")
#                 tmp_varLabel2 = varLabel2_elem.get_attribute('textContent')
#                 try: 
#                     tmp_swatch_image2 = var_elem2.find_element(By.XPATH,"./div[2]/div/@class[contains(.,'active')]/parent::div/img").get_attribute('src')

#                 except:
#                     tmp_swatch_image1 =""
#                 extract_data(cat1, cat2)

### -------------- refactored get_variants()
def get_variants(cat1, cat2):
    global tmp_var1, tmp_var2, tmp_varLabel1, tmp_varLabel2, tmp_swatch_image1, tmp_swatch_image2

    count_var_elem = driver.find_elements(By.XPATH, variants_xpath)
    count_var = len(count_var_elem)

    if count_var == 1:
        process_single_variant(cat1, cat2)
    elif count_var == 2:
        process_two_variants(cat1, cat2)


def scroll_to_top():
    driver.execute_script("window.scrollTo(0, 0)")


def view_more_specs():
    # sleep(1)
    viewMoreSpecs()


def process_single_variant(cat1, cat2):
    var_elem1 = get_var_elem1()
    var_elem1_lst = get_var_elem1_lst(var_elem1)

    for i in range(len(var_elem1_lst)):
        scroll_to_top()
        var_elem1 = get_var_elem1()

        if not var_elem1:
            break

        click_elem1(var_elem1, i)
        view_more_specs()

        var_elem1 = get_var_elem1()

        if not var_elem1:
            break

        extract_variant1_data(var_elem1)
        extract_data(cat1, cat2)


def process_two_variants(cat1, cat2):
    var_elem1 = get_var_elem1()
    var_elem1_lst = get_var_elem1_lst(var_elem1)

    for i in range(len(var_elem1_lst)):
        scroll_to_top()
        var_elem1 = get_var_elem1()

        if not var_elem1:
            break

        elem = click_elem1(var_elem1, i)
        if elem is True:
            var_elem1 = get_var_elem1()
        else:
            break
        # view_more_specs()

        if not var_elem1:
            break

        extract_variant1_data(var_elem1)

        var_elem2 = get_var_elem2()

        if not var_elem2:
            break

        var_elem2_lst = get_var_elem2_lst(var_elem2)

        for i in range(len(var_elem2_lst)):
            scroll_to_top()

            click_elem2(var_elem2, i)
            # view_more_specs()

            var_elem2 = get_var_elem2()

            if not var_elem2:
                break

            extract_variant2_data(var_elem2)
            extract_data(cat1, cat2)


def get_var_elem1():
    try:
        return driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
    except:
        return None


def get_var_elem1_lst(var_elem1):
    return var_elem1.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")


def click_elem1(var_elem1, i):
    try:
        var_elem1.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")[i].click()
        view_more_specs()
        return True
    except:
        print('disabled element skipping click event')
        return False


def extract_variant1_data(var_elem1):
    global tmp_var1, tmp_varLabel1, tmp_swatch_image1
    tmp_var1 = var_elem1.find_element(By.XPATH, "./div[1]/span[2]").get_attribute("textContent")
    varLabel1_elem = var_elem1.find_element(By.XPATH, "./div[1]/span[1]")
    tmp_varLabel1 = varLabel1_elem.get_attribute('textContent')
    try:
        tmp_swatch_image1 = var_elem1.find_element(By.XPATH, "./div[2]/div/@class[contains(.,'active')]/parent::div/img").get_attribute('src')
    except:
        tmp_swatch_image1 = ""

def get_var_elem2():
    try:
        return driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[2]")
    except:
        return None

def get_var_elem2_lst(var_elem2):
    return var_elem2.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")

def click_elem2(var_elem2, i):
    try:
        var_elem2.find_elements(By.XPATH, "./div[2]/div/@class[not(contains(.,'disabled'))]/parent::div")[i].click()
        view_more_specs()
        return True
    except:
        print('disabled element skipping click event')
        return False

def extract_variant2_data(var_elem2):
    global tmp_var2, tmp_varLabel2, tmp_swatch_image2
    tmp_var2 = var_elem2.find_element(By.XPATH, "./div[1]/span[2]").get_attribute("textContent")
    varLabel2_elem = var_elem2.find_element(By.XPATH, "./div[1]/span[1]")
    tmp_varLabel2 = varLabel2_elem.get_attribute('textContent')
    try:
        tmp_swatch_image2 = var_elem2.find_element(By.XPATH, "./div[2]/div/@class[contains(.,'active')]/parent::div/img").get_attribute('src')
    except:
        tmp_swatch_image2 = ""
########----------- end of get_variants()

def save():
    #save to csv
    with open(f'{filename}.csv', 'w', newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=product_info.keys())
        writer.writeheader()
        writer.writerows(products)
    logging.info(f"Export to CSV file {filename} is finished.")

def allowCookie():
    cookie_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, cookie_xpath))
        )
    cookie_btn.click()
 
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
    driver = chr_driver()

    if TEST_MODE is True:
        print('RUNNING ON TEST MODE')
        scrape_prod_links()
        
    else:
        logging.debug(f'Parsing initial URL: {initial_url}')
        driver.get(initial_url)
        sleep(40)      
        # login(un,pw)
        # allowCookie()
        category1_urls = scrape_initial_page()
        get_category_links()
        get_prod_links()
        scrape_prod_links()
    save()
    driver.quit()

