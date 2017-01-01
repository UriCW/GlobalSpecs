from bs4 import BeautifulSoup as bs
import json
"""
Extracts the relevant parts from an html or a json
"""
class Suppliers: 
    def get(self,html):
      """
      Returns an index of suppliers from an html page
      suppliers=[
      {
        'supplier' : ''
        'link'      : ''
        'harvested' : False
      },...
      ]
      """
      ret=[]
      soup = bs(html,'html.parser')
      suppliers=soup.findAll("tr",attrs={"class":"result-item"})
      if suppliers is None: return None #This is past the last page
      for s in suppliers:
        a=s.find("a")
        link=a['href']
        name=a.getText().strip()
        entry={
          "supplier":str(name),
          "link":str(link),
          "harvested":False
        }
        ret.append(entry)
      return ret

class Industrial: 
    def get(self,html):
        ret=[] #Stop using self.ProdActs!
        soup = bs(html,'html.parser')
        div=soup.find("div",attrs={'id':'keyword-results'})
        links=div.findAll('a')
        for link in links:
          category=link.getText().strip()
          url=link['href']
          entry={
            "title":str(category),
            "url":str(url),
            "harvested":False
          }
          ret.append(entry)
        return ret

class Catalogs: 
    def get_products(self,json_contents):
        #Gets the products from a category page or another catalog page
        html=json.loads(json_contents)["RESULTS"] #The contents are in the json element, inside some html tags
        soup = bs(html,"html.parser")
        ret=[]
        for a in soup.findAll("a",attrs={"class":"product-name"}):
            if "partspecs?" in a['href']: #A product
                catalog_entry={
                    'title':a.getText(),
                    'uri':a['href'],
                    'comp':a['href'].split("comp=")[1].split("&")[0],
                    'vid':a['href'].split("vid=")[1].split("&")[0],
                    'partId':a['href'].split("partId=")[1].split("&")[0],
                    'harvested':False
                }
                ret.append(catalog_entry)
        return ret

    def get_catalogs(self,json_contents):

        #Gets the catalogs from a category page or another catalog page
        html=json.loads(json_contents)["RESULTS"] #The contents are in the json element, inside some html tags
        soup = bs(html,"html.parser")
        ret=[]
        for a in soup.findAll("a",attrs={"class":"product-name"}):
            if "search/products" in a['href']: #A catalog
                catalog_entry={
                    'title':a.getText(),
                    'uri':a['href'],
                    'comp':a['href'].split("comp=")[1].split("&")[0],
                    'cat_id':a['href'].split("comp=")[1].split("&")[0],
                    'vid':a['href'].split("vid=")[1].split("&")[0],
                    'harvested':False
                }
                ret.append(catalog_entry)
        return ret
class Categories: 
    def getFromFormatA(self,content):
        """
        e.g /industrial-directory/audio_amplifier_schematic
        I Hate this!
        @TODO change param from ?show=suppliers to ?show=products
        """
        ret=[]
        for i,link in enumerate( content.findAll("a",attrs={'class':'search-result-title'}) ):
            title=link.getText().strip()
            title=' '.join(title.split())
            url=link["href"]
            cid=url.split("?comp=")[-1]
            #prt( id+" : "+title+":"+url)
            #prt( str(link.prettify() ) )
            ret.append(
                {
                    'category_id':cid,
                    'title':title,
                    'url':url,
                    'product_page':None,
                    'harvested':False
                }
            )
        return ret 

    def getFromFormatB(self,content):
        """
        e.g. /industrial-directory/Acrylic_Wrap
        I Hate this more!
        """
        ret=[]
        for item in content.findAll("li",attrs={'class':'part-summary'}):
            title=item.find("div",attrs={"class":"part-name"}).getText().strip()
            title=' '.join(title.split())
            url=item.find("div",attrs={"class":"part-name"}).find("a")["href"]
            ret.append(
                {
                    'category_id':None,
                    'title':title,
                    'url':url,
                    'product_page':url,
                    'harvested':False
                }
            )
        return ret

    def get(self,html):
        #Takes an HTML page, and tried to extract the Categories page or Product Links,
        #This depends on the HTML page
        #Raises exception when not a known HTML format, d/k what to do next stop everything
        soup=bs(html,'html.parser')
        cats=[]
        content=soup.find("div",attrs={"id":"products"})
        if content is not None:
           cats = self.getFromFormatA(content)
           return cats
        content=soup.find("div",attrs={"class":"simple-section-wrapper"})
        if content is not None:
            cats=self.getFromFormatB(content)
            return cats
        raise(Exception("Unknown Categories Directory HTML Format"))
