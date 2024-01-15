# -*- coding: utf-8 -*-


import requests
from dotenv import load_dotenv
import os

def image_api(message,type):
    
    #img_data = open(message,'rb')
    #psurl = 'https://ranaka-amk.com/img_stock.php'
    #r = requests.post(psurl,img_data)
    apikey = os.environ['NORIKO_API_KEY'] 
    #api_url = "https://api.a3rt.recruit-tech.co.jp/image_search/v1/search_by_image"
    api_url = "https://api.a3rt.recruit.co.jp/image_search/v1/search_by_image"
    image = "https://tondabayashi.sakura.ne.jp/drone/img.jpg"#"https://reachstock.jp/assets/img/report/apple_01.jpg"#画像パスを入れる
    payload = {"apikey": apikey, "query": 0, "image": image}

    response = requests.get(api_url,payload)
    data = response.json()
    data_img = data["result"]["img"]


    #データのurl部分を抽出して
    i = 0
    for img in data_img[i]:
        print(i+1)
        url_list = dict(data_img[i])
        print (data["result"]["txt"][i])
        url_list['url']
        i+=1
    try:
        if type == 1:
            return url_list['url']
        if type == 2:
            return data["result"]["txt"][0]
    except:
        return print("response.status_code")

def main():
         message = 0
         image_api(message,2)

if __name__ == "__main__":
     main()
