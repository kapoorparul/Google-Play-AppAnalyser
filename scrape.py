from __future__ import print_function
import webbrowser
import requests 
from bs4 import BeautifulSoup 
from urllib2 import urlopen,Request #used to retrieve url info
import sys
import os
from operator import itemgetter
App={}
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} #To spoof Python

def search(name):
    Name=''
    for i in name.split():
        Name+=i+'%20'
    Name=Name[:len(Name)-3]    
    query=requests.get('https://play.google.com/store/search?q='+Name+'&hl=en',headers=headers)
    s=BeautifulSoup(query.text,"html.parser")#search app
    #print(s.prettify())
    l=s.find("div",{"class":"card no-rationale square-cover apps small"}).get('data-docid')
    title = s.select_one('a.title').attrs['title']#title
    print("title: "+title)
    App['title']=title
    plink="https://play.google.com/store/apps/details?id="+l
    query2=requests.get('https://play.google.com/store/apps/details?id='+l,headers)#app details
    #print("the url :"+plink)
    global pagesoup
    pagesoup=BeautifulSoup(query2.text,"html.parser")
    #print(pagesoup.prettify())
    return(App,pagesoup)
    
def app_details(pagesoup):
       
    des=pagesoup.findAll("div",{"jsname":"C4s9Ed"})#description
    descrip=''
    for d in des:
        #print(d)
        description=d.get_text().strip()
        #print(description)
        descrip=descrip+description
    App['Desc']=descrip
    rating=pagesoup.findAll("div",{"class":"score"})#current rating 
    for rate in rating:
        zz=rate.get_text()
    
    App['Rating']=zz
    imgurl=pagesoup.findAll("img",{"class":"cover-image","alt":"Cover art"})#img url
    for image in imgurl:
        iu=image.get('src')
    imageurl="https:"+iu
    App['ImageUrl']=imageurl
    try:                                                            #price
        price = pagesoup.select_one('span.display-price').string
    except AttributeError:
        try:
            # Pre-register apps 'Coming Soon'
            price = pagesoup.select_one('.price').string
        except AttributeError:
            # Country restricted, no price or buttons shown
            price = 'Not Available'

    free = (price == 'Free')
    if free is True:
        price = '0'
    App['Price']=price
    category = [c.attrs['href'].split('/')[-1] for c in pagesoup.select('.category')]#category
    App['category']=category
    print(category)
    #print(App)
    return(App)

    
   
    
def appReviews(pagesoup):
    index=1
    rev=[]
    rev=pagesoup.findAll("div",{"class":"review-text","class":"review-body with-review-wrapper"})#40 top reviews
    try:
        for review in rev:
            
            yy=review.get_text()
            yy=yy[:-13].encode('utf-8')
            rev.append(yy)
            
            index+=1
    except AttributeError:
        pass
    rev=rev[40:]
    return(rev)

def AdditionalInfo(pagesoup):
    addinf=pagesoup.findAll("div",{"class":"details-section metadata"})#additional info
    recent_changes = "\n".join([x.string.strip() for x in pagesoup.select('div.recent-change')])
    top_developer = bool(pagesoup.select_one('meta[itemprop="topDeveloperBadgeUrl"]'))
    editors_choice = bool(pagesoup.select_one('meta[itemprop="editorsChoiceBadgeUrl"]'))
    additional_info = pagesoup.select_one('div.metadata div.details-section-contents')
    updated = additional_info.select_one('div[itemprop="datePublished"]')
    if updated:
        updated = updated.string
        App['updated']=updated

    size = additional_info.select_one('div[itemprop="fileSize"]')
    if size:
        size = size.string.strip()
        App['size']=size

    try:
         installs = [int(n.replace(',', '')) for n in additional_info.select_one(
                'div[itemprop="numDownloads"]').string.strip().split(" - ")]
         App['installs']=installs
    except AttributeError:
        installs = [0, 0]
        App['installs']=installs
    

    current_version = additional_info.select_one('div[itemprop="softwareVersion"]')
    if current_version:
        try:
            current_version = current_version.string.strip()
            
        except AttributeError:
            current_version = current_version.span.string.strip()
    App['current_version']=current_version
    required_android_version = additional_info.select_one('div[itemprop="operatingSystems"]')
    if required_android_version:
        required_android_version = required_android_version.string.strip()
        App['a_version']=required_android_version

    content_rating = additional_info.select_one('div[itemprop="contentRating"]')
    if content_rating:
        content_rating = content_rating.string
        App['c_rating']=content_rating

    meta_info = additional_info.select('.title')
    meta_info_titles = [x.string.strip() for x in meta_info]
    try:
        i_elements_index = meta_info_titles.index('Interactive Elements')
        interactive_elements = meta_info[i_elements_index].next_sibling.next_sibling.string.split(', ')
    except ValueError:
        interactive_elements = []
        pass

    offers_iap = bool(pagesoup.select_one('div.inapp-msg'))
    iap_range = None
    if offers_iap:
        try:
            iap_price_index = meta_info_titles.index('In-app Products')
            iap_range = meta_info[iap_price_index].next_sibling.next_sibling.string
        except ValueError:
            iap_range = 'Not Available'
            pass
    App['iap_range']=iap_range
    developer = pagesoup.select_one('span[itemprop="name"]').string
    App['deve']=developer
    dev_id = pagesoup.select_one('a.document-subtitle.primary').attrs['href'].split('=')[1]
    developer_id = dev_id if dev_id.isdigit() else None
    App['devId']=developer_id
    try:
        developer_email = additional_info.select_one('a[href^="mailto"]').attrs['href'].split(":")[1]
    except AttributeError:
        developer_email = None
    App['devMail']=developer_email
    developer_url = additional_info.select_one('a[href^="https://www.google.com"]')
    if developer_url:
        developer_url = developer_url.attrs['href'].split("&")[0].split("=")[1]
    App['devUrl']=developer_url
    developer_address = additional_info.select_one('.physical-address')
    if developer_address:
        developer_address = developer_address.string
    App['devAdr']=developer_address
    
    return App
    
def SimilarApps(pagesoup):
    surl=pagesoup.findAll("a",{"data-uitype":"291"})[0]#similar apps url
    simiurl=surl.get('href')
   
    query3=requests.get('https://play.google.com'+simiurl,headers)
    Spagesoup=BeautifulSoup(query3.text,"html.parser")
    title = Spagesoup.select('a.title')
    print(title[1].get('title'))
    i=0
    Simi=[]
    Simi.append([])
    Simi.append([])
    Simi.append([])
    Simi.append([])
    Simi.append([])
    sameapp=Spagesoup.findAll("a",{"data-uitype":"500"})#links of all similar apps
    for sa in sameapp:
        title = Spagesoup.select('a.title')
        t=title[i].get('title')
        slink=sa.get('href')
        simiLink="https://play.google.com"+slink
        query4=requests.get(simiLink,headers)
        Appsoup=BeautifulSoup(query4.text,'html.parser')
        temp=app_details(Appsoup)
        temp['title']=t
        Simi[i].append(temp['category'])
        Simi[i].append(temp['title'])
        Simi[i].append(temp['Price'])
        Simi[i].append(temp['Rating'])
        Simi[i].append(temp['ImageUrl'])
        Simi[i].append(temp['Desc'])
        i=i+1
        if i==5:
            break
    return(Simi)
    
def top_App(category,n):
    query=requests.get('https://play.google.com/store/apps/category/'+category,headers=headers)
    top=[]
    top.append([])
    top.append([])
    top.append([])
    top.append([])
    top.append([])
    top.append([])
    top.append([])
    top.append([])
  
    s=BeautifulSoup(query.text,"html.parser")
    if n=='1' or n=='0':
        for i in range(7,15):
            for dd in s.findAll("div",{"class":"details"})[i:i+1]:
                soup2 = BeautifulSoup(str(dd),"html.parser")
                t=soup2.find("a",{"class":"title"})
                t=t.get_text().strip()
                top[i-7].append(t)
                p=soup2.find("span" ,{"class":"display-price"})
                p=p.get_text().strip()
                top[i-7].append(p)
                d=soup2.find("div",{"class":"description"})
                d=d.get_text().strip()
                top[i-7].append(d)
                l=soup2.find("a",{"class":"card-click-target"})
                l=l.get('href').strip()
                top[i-7].append(l)
        
            for dd2 in s .findAll("div",{"class":"tiny-star star-rating-non-editable-container"})[i:i+1]:
                r=dd2.get('aria-label')
                rating=r[6:9]
                top[i-7].append(rating)
        top.sort(key=itemgetter(4),reverse=True)
        return top
        
    if n=='2':
        for i in range(17,25):
            for dd in s.findAll("div",{"class":"details"})[i:i+1]:
                soup2 = BeautifulSoup(str(dd),"html.parser")
                t=soup2.find("a",{"class":"title"})
                t=t.get_text().strip()
                top[i-17].append(t)
                p=soup2.find("span" ,{"class":"display-price"})
                p=p.get_text().strip()
                top[i-17].append(p)
                d=soup2.find("div",{"class":"description"})
                d=d.get_text().strip()
                top[i-17].append(d)
                l=soup2.find("a",{"class":"card-click-target"})
                l=l.get('href').strip()
                top[i-17].append(l)
        
            for dd2 in s .findAll("div",{"class":"tiny-star star-rating-non-editable-container"})[i:i+1]:
                r=dd2.get('aria-label')
                rating=r[6:9]
                top[i-17].append(rating)
    
    
        top.sort(key=itemgetter(4),reverse=True)
        return top
    if n=='3':
        for i in range(27,35):
            for dd in s.findAll("div",{"class":"details"})[i:i+1]:
                soup2 = BeautifulSoup(str(dd),"html.parser")
                t=soup2.find("a",{"class":"title"})
                t=t.get_text().strip()
                top[i-27].append(t)
                p=soup2.find("span" ,{"class":"display-price"})
                p=p.get_text().strip()
                top[i-27].append(p)
                d=soup2.find("div",{"class":"description"})
                d=d.get_text().strip()
                top[i-27].append(d)
                l=soup2.find("a",{"class":"card-click-target"})
                l=l.get('href').strip()
                top[i-27].append(l)
        
            for dd2 in s .findAll("div",{"class":"tiny-star star-rating-non-editable-container"})[i:i+1]:
                r=dd2.get('aria-label')
                rating=r[6:9]
                #print(rating)
                top[i-27].append(rating)
        top.sort(key=itemgetter(4),reverse=True)
        return top
    if n=='4':
        for i in range(37,45):
            for dd in s.findAll("div",{"class":"details"})[i:i+1]:
                soup2 = BeautifulSoup(str(dd),"html.parser")
                t=soup2.find("a",{"class":"title"})
                t=t.get_text().strip()
                top[i-37].append(t)
                p=soup2.find("span" ,{"class":"display-price"})
                p=p.get_text().strip()
                top[i-37].append(p)
                d=soup2.find("div",{"class":"description"})
                d=d.get_text().strip()
                top[i-37].append(d)
                l=soup2.find("a",{"class":"card-click-target"})
                l=l.get('href').strip()
                top[i-37].append(l)
        
            for dd2 in s .findAll("div",{"class":"tiny-star star-rating-non-editable-container"})[i:i+1]:
                r=dd2.get('aria-label')
                rating=r[6:9]
                top[i-37].append(rating)
        top.sort(key=itemgetter(4),reverse=True)
        return top


    
    

if __name__ == "__main__":
    name=raw_input("Name the app: ")
    
    
    res=search(name)
    print(res)
    print("Select category")
    print("1.Education")
    print("2.Social")
    print("3.Lifestyle")
    print("4.Games")
    r=raw_input()
    if(r=='1'):
        TApp=top_App('EDUCATION')
    if(r=='2'):
        TAapp=top_App('SOCIAL')
    if(r=='3'):
        TApp=top_App('LIFESTYLE')
    if(r=='4'):
        subcat=raw_input("Select subcategory\n 1.Action \n2.Adventure \n3.Arcade")
        if(subcat=='1'):
            TApp=top_App('GAME_ACTION')
        if(subcat=='2'):
            TApp=top_App('GAME_ADVENTURE')
        if(subcat=='3'):
            TApp=top_App('GAME_ARCADE')
    print(TApp)
    
