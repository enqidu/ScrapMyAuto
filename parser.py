from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import shutil
import requests
import os
import csv
import sys

# import Image


fields = ['ID',	'Manufacturer',	'Model', 'Category', 'Mileage',	'Gear box type', 'Doors', 'Wheel', 'Color', 'Interior color', 'VIN', 'Leather interior', 'Price', 'Customs']
def_url = 'https://www.myauto.ge/en/s/00/0/00/00/00/00/00/cars?stype=0&currency_id=3&det_search=0&ord=7&category_id=m0&keyword=&page='
filename = "myauto data.csv"

num_of_pages = 4089
current_auto_id = 1


def download_image(url, filename):
    img_response = requests.get(url, stream=True)
    file = open("./Dataset/{}/{}.jpg".format(current_auto_id, filename), 'wb')
    img_response.raw.decode_content = True
    shutil.copyfileobj(img_response.raw, file)
    del img_response

def parse_auto_info(url):
    my_dict = {'ID':str(current_auto_id), 'Manufacturer':'None', 'Model':'None', 'Category':'None', 'Mileage':'None', 'Gear box type':'None', 'Doors':'None', 'Wheel':'None', 'Color':'None', 'Interior color':'None', 'VIN':'None', 'Leather interior':'None', 'Price':'None', 'Customs':'None'}
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    if (page_soup is None): return

    # parsing car price and cutoms price
    detail_container = page_soup.find('div',  {"class": "container-main"})
    if (detail_container is None): return
    car_price_container = detail_container.find("div", {"class": "detail-info-container"})

    if (car_price_container is None): return

    if (len(car_price_container.findAll("span", {"class": "car-price"})) < 2): return

    customs_price = 'Cleared'

    car_price = car_price_container.findAll("span", {"class": "car-price"})[1].text
    customs_price_levy = car_price_container.find("div", {"class": "levy"})
    if (customs_price_levy is not None and customs_price_levy.find("span", {"class":"hide"}) is not None):
        customs_price = customs_price_levy.find("span", {"class":"hide"}).text

    my_dict['Price'] = car_price
    my_dict['Customs'] = customs_price
    # Downloading images
    image_container = detail_container.find('div', {"class": "thumbnail-wrapper"}).div
    if (image_container  is not None): 
        child_imgs = image_container.findChildren("div" , recursive=False)
        img_id = 1

        new_dir = './Dataset/{}'.format(current_auto_id)
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        else:
            print('Something wrong')
        for child in child_imgs:
            # print(child)
            child_content = child.findChildren(recursive=False)
            if (child_content is None): continue
            url = child_content[0]['src']
            if (url is None): continue
            # print(url)
            download_image(url, img_id)
            img_id += 1


    table = page_soup.findAll("table", {"class": "detail-car-table"})[0]
    left_entries = table.findAll("th", {"class": "th-left"})
    right_entries = table.findAll("th", {"class": "th-right"})

    entries_l = left_entries + right_entries

    
    for entry in entries_l:
        value_l = []
        value_l += entry.findAll("div", {"class": "th-key"})
        value_l += entry.findAll("div", {"class": "th-value"})
        if (len(value_l) != 2): continue
        
        key_type = value_l[0].text.strip()
        if (key_type == 'Manufacturer'):
            my_dict['Manufacturer'] = value_l[1].text.strip()
        elif (key_type == 'Model'):
            my_dict['Model'] = value_l[1].text.strip()
        elif (key_type == 'Category'):
            my_dict['Category'] = value_l[1].text.strip()
        elif (key_type == 'Mileage'):
            my_dict['Mileage'] = value_l[1].text.strip()
        elif (key_type == 'Gear box type'):
            my_dict['Gear box type'] = value_l[1].text.strip()
        elif (key_type == 'Doors'):
            my_dict['Doors'] = value_l[1].text.strip()
        elif (key_type == 'Wheel'):
            my_dict['Wheel'] = value_l[1].text.strip()
        elif (key_type == 'Color'):
            my_dict['Color'] = value_l[1].text.strip()
        elif (key_type == 'Interior color'):
            my_dict['Interior color'] = value_l[1].text.strip()
        elif (key_type == 'VIN'):
            my_dict['VIN'] = value_l[1].text.strip()
        elif (key_type == 'Leather interior'):
            if len(value_l[1].i.attrs['class']) >= 2:
                if value_l[1].i.attrs['class'][1] == 'fa-check':
                    my_dict['Leather interior'] = '1'
                else:
                    my_dict['Leather interior'] = '0'

    return my_dict


def parse_autos_page(url):
    print('--on car pages url:  {}'.format(url))
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    main_container = page_soup.find('div',  {"class": "container-main"})
    detail_container = main_container.findAll('div',  {"class": "container-main"})
    search_lists_container = main_container.find('div',  {"class": "search-lists-container"})
    autos_infos = search_lists_container.findChildren('div', recursive=False)
    counter = 0
    infos_list = []
    for auto_info in autos_infos:
        auto_info_container = auto_info.find('div',  {"class": "car-name-left"})
        if (auto_info_container == None): continue
        auto_url = auto_info_container.findChildren(recursive=False)
        if (auto_url == None): continue
        url_dict = auto_url[0].findChildren()
        if (url_dict == None): continue
        auto_info_url = url_dict[0]['href']
        print('------------- current car : {}'.format(auto_info_url))
        if (auto_info_url != None):
            infos_list.append(parse_auto_info(auto_info_url))
            global current_auto_id
            current_auto_id += 1
    return infos_list





if __name__ == "__main__":
    if (len(sys.argv) == 4):
        def_url = sys.argv[1]
        num_of_pages = int(sys.argv[2])
        filename = sys.argv[3]
    for i in range(189, num_of_pages-1):
        url = def_url + str(i)
        infos_list = parse_autos_page(url)
        with open(filename, 'a') as csvfile:  
            # creating a csv dict writer object  
            writer = csv.DictWriter(csvfile, fieldnames = fields)
            writer.writerows(infos_list)  
