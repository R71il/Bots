from bs4 import BeautifulSoup
from typing import Union
import requests
import requests.exceptions
from random import choice

mycima = "https://www.1-wee-ciima.shop"

def searcher(name : str, kind : str) -> Union[str, tuple[list, list]]:
    headers : dict = {"user-agent" : "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}
    try:
        soup : BeautifulSoup = BeautifulSoup(requests.get(mycima, headers=headers).content,"html.parser")
    except requests.exceptions.ConnectionError :
        return "عذرا تم ايقاف البحث مؤقتا ❌️"
    domain : str = soup.find("div", {"class" : "RightSideFlex"}).find("a").get("href")
    print(domain)
    if kind == "movie":
      soup : BeautifulSoup = BeautifulSoup(requests.get(f"{domain}/search/{name}").content,"html.parser")
    else:
      soup : BeautifulSoup = BeautifulSoup(requests.get(f"{domain}/search/{name}/list/series").content,"html.parser")     
    result : list = soup.find_all("div", { "class" : "Thumb--GridItem"})
    if len(result) > 0:
        titles : list = []
        urls : list = []
        for item in result:
            titles.append(item.text)
        for item in result:
            urls.append(item.contents[0].get("href"))
        return titles, urls
    
    typness: str  = "فيلم" if kind == "movie" else "مسلسل"
    no_result : str = f"🔴 | عذرًا لايوجد {typness} بهذا الإسم \"{name}\""
    return no_result
    
def cleaner(name : str, kind : str) -> tuple[list, list]:
    search_words : list = []
    for item in name.split(" ")[1:]:
      if item.endswith("ه"):
        item: str = item[:-1] + "ة"
      
      if item.startswith("الا"):
          item: str = "الأ" + item[3:]
          
      search_words.append(item)
    clean_name : str = " ".join(search_words)
    result : tuple = searcher(clean_name, kind)
    if len(result) == 2:
      titles : list = result[0]
      urls : list = result[1]
      print(urls)
      return titles, urls
    no_result : str = result
    return no_result

def content_info(url : str, kind : str)-> tuple :
  soup : BeautifulSoup = BeautifulSoup(requests.get(url).content, "html.parser")
  title : str = soup.find("div", {"class" : "Title--Content--Single-begin"}).text.strip()
  details : list = soup.find("ul", {"class" : "Terms--Content--Single-begin"}).find_all("li")
  
  details_text : str = f" العنوان : {title}\n\n"
  for item in details:
    text : str= f" {item.contents[0].text} : {item.contents[1].text}\n\n"
    details_text += text
    
  if kind == "for one":
    try:
        poster : str = soup.find("singlecontainerright").contents[0].get("data-lazy-style").split("(")[1].split(")")[0]
    except AttributeError:
        poster : str = soup.find("singlecontainerright").contents[0].get("style").split("(")[1].split(")")[0]

    try:
        watching_url = soup.find("iframe").get("data-lazy-src")
    except:
        watching_url = soup.find("iframe").get("src")
      
    return details_text, poster, watching_url, soup
  
  poster : str = soup.find("singlecontainerright").contents[0].get("style").split("(")[1].split(")")[0]
  seasons_tags : list = soup.find("div", {"class" : "Seasons--Episodes"})
  return details_text, poster, seasons_tags, soup

def season_episodes(seasons_tags: list, season_num: list) -> tuple[list, list]:
  seasons_url : list = seasons_tags.contents[0].find_all("a")
  soup : BeautifulSoup = BeautifulSoup(requests.get(seasons_url[season_num].get("href")).content,  "html.parser")            
  episodes_urls : list = soup.find("div", {"class" : "Seasons--Episodes"}).contents[1].find_all("a")
  episodes_nums : list = real_episodes_nums(episodes_urls)
  
  return episodes_urls, episodes_nums
  
def episodes(season) -> tuple[list, list]:
    episodes_tags : list = season.contents[0].find_all("a")
    episodes_tags.reverse()
    episode_urls : list = []
    for item in episodes_tags:
      episode_urls.append(item.get("href"))
    episodes_nums : list = real_episodes_nums(episodes_tags)
    
    return episode_urls, episodes_nums

def downloader(soup : BeautifulSoup) -> tuple[list, list]:
  download_links : list = soup.find("div", { "class" : "Download--Wecima--Single"}).contents[1].find_all("li")
  qualities : list = [quality.text for quality in download_links]
  qualities_URLs : list = [quality.find("a").get("href") for quality in download_links]
  
  return qualities_URLs, qualities

def real_episodes_nums(episodes_tags) -> list:
    episodes_nums : list = []
    nums = ("1", "2", "3", "3", "4", "5", "6", "7", "8", "9")
    for i in range(0, len(episodes_tags)):
      href : str = episodes_tags[i].get("href")
      if episodes_tags[i].get("class")[0] != "hoverable":
        episodes_nums.append(href.split("-")[-1].split("/")[0])
      else:
        for num in href.split("-")[-2:]:
          if num.startswith(nums) and num.endswith("/"):
            episodes_nums.append(num.split("/")[0])
          elif num.startswith(nums):
            episodes_nums.append(num)
            
    return episodes_nums