from bs4 import BeautifulSoup as bs
class HarvestSupplierProfile:
    """
    Harvest data for a single Supplier profile.
    Stores result of harvest in 
    ProFile = {
      'info'    : {}
      'about': '',
      'catalog': '',
      'news': '',
      'announcements': ...
      'articles': ...
      'videos': ...
      
    }
    """
    ProFile={}
    
    def getAbout(self,html):
      soup=bs(html,'html.parser')
      content=soup.find("div",attrs={'id':'main-content'})

      title=content.find("div",attrs={'class':'page-title-container'}).find("h1").getText()
      profile_text=content.find("div",attrs={'id':'sp-profile-text'})
      about_video=content.find("div",attrs={'class':'sup-about-video'}).find('iframe')['src']
      about={
        'title':title,
        'text':profile_text,
        'video':about_video
      }
      return about
    def getCatalog(self,html):
      soup=bs(html,'html.parser')
      content=soup.find("div",attrs={'id':'catalog-area-list'})
      catalog=[]
      for div in content.findAll('div',attrs={'class','catalog-area'}):
        url=div.find('a')['href']
        img=div.find('img')['src']
        title=div.find('div',attrs={'class':'area-text'}).find('a').getText().strip()
        subtext=div.find('div',attrs={'class':'subtext'}).getText().strip()
        product={
          'url':url,
          'img':img,
          'title':title,
          'subtext':subtext
        }
        catalog.append(product);
      return catalog
    def getNews(self,html):
      soup=bs(html,'html.parser')
      content=soup.find("div",attrs={'class':'area-listing'})
      news=[]
      for item in content.findAll('div',attrs={'class','area-listing-item'}):
        date=item.find('div',attrs={'class':'left'}).getText().strip()
        title=item.find("a",attrs={'class':'item-title'}).getText().strip()
        url=item.find("a",attrs={'class':'item-title'})['href']
        desc=item.find("p").getText().strip()
        news_item={
          'title':title,
          'date':date,
          'link':url,
          'desc':desc
        }
        news.append(news_item)
      return news
      
    def getAnnouncements(self,html):
      soup = bs(html,"html.parser")
      #There is an extra </div> which breaks everything.
      #Iterate 4 times instead and then join arrays (and hope they are in the same order)
      titles=[]
      descriptions=[]
      images=[]
      urls=[]
      for title in soup.findAll("div",attrs={"class","item-title-container"}):
          titles.append(title.getText().strip() )
          link=title.find("a")['href']
          urls.append(link)
      for desc in soup.findAll("span",attrs={"class","short-desc"}):
          descriptions.append(desc.getText().strip() )
      for img in soup.findAll("div",attrs={"class":"pa-img-wrapper"}):
          src=img.find("img")['src']
          images.append(src)
      #Now put in dictionary
      announcements=[]
      for i in range(0,len(titles)):
          item={}
          item['title']=titles[i]
          item['description']=descriptions[i]
          item['img']=images[i]
          item['url']=urls[i]
          announcements.append(item)
      return(announcements)

    def getArticles(self,html):
      """
      Gets a list of article headers from an html string
      returns
          Articles=[
              {
                  "title":""
                  "description":""
                  "subtext":""
                  "url":""
              },
              {},...
          ]
      """
      Articles=[]
      soup=bs(html,'html.parser')
      content=soup.find("div",attrs={'class':'area-listing'})
      items=content.findAll("div",attrs={'class':'area-listing-item'})
      for item in items:
          title=item.find('a',attrs={'class':'item-title'}).getText().strip()
          url=item.find('a',attrs={'class':'item-title'})['href']
          subtext=item.find("b").getText().strip() 
          desc=item.find("div",attrs={'class':'last'}).find("div").getText().strip()#TODO cleanup
          Articles.append(
              {
                  'title':title,
                  'url':url,
                  'subtext':subtext,
                  'description':desc
              }
          )
      return Articles

    def getVideos(self,html):
        """
        Gets a list of article headers from an html string
        returns
            Videos=[
                {
                    "title":""
                    "description":""
                    "subtext":""
                    "url":""
                },
                {},...
            ]
        """
        Videos=[]
        soup=bs(html,'html.parser')
        content=soup.find("div",attrs={'id':'featured-videos'})
        #TODO (This is just the code for Article getting, needs the correct divs ids classes etc)
        for i,vid in enumerate(content.findAll("div",attrs={'class':'videoPage'})):
            title=vid.find("div",attrs={"class":"feature-title"}).getText().strip()
            desc=vid.find("p")
            subtext=vid.find("div",attrs={"class":"classification"})
            #The above don't have a shared container, take from loop index i
            url = content.findAll("iframe")[i]['src']
            if subtext is not None:
                subtext=subtext.getText().strip()
            if desc is not None:
                desc=desc.getText().strip()
            Videos.append(
                { 
                    'title':title,
                    'description':desc,
                    'subtext':subtext,
                    'url':url
                }
            )
        return Videos




    def getInfo(self,html):
        """
        Gets the info/sidebar for a supplier
        returns
        {
            'content': HTML of the <div id=supplier-info>    
        }
        """
        soup = bs(html,"html.parser")
        content = soup.find("div",attrs={"id":"supplier-info"})
        return {
            'content'   :   str(content),
        }

    def get(self,htmls={} ):
        """
        Takes a collection of HTMLs from a supplier profile, 
        constructs and returns a supplier profile dictionary
        arguments
            htmls={
                'about'='',
                'catalog'='',
                'news'='',
                'announcements'='',
                'articles'='',
                'videos'='',
            }
        return
            ProFile={
            }
        """
        categories=['about','catalog','news','productannouncements','techarticles','videos']
        for category in categories:
          if category =="about":
            about=self.getAbout( htmls['about'] )
            self.ProFile['about']=about
            self.ProFile['info']=self.getInfo(htmls['about']) #Do this once
          if category =="catalog":
            catalog=self.getCatalog(htmls['catalog'])
            self.ProFile['catalog']=catalog
          if category =="news":
            news=self.getNews(htmls['news'])
            self.ProFile['news']=news
          if category =="productannouncements":
            announce=self.getAnnouncements(htmls['accouncements'])
            self.ProFile['announcements']=announce
          if category =="techarticles":
            arts=self.getArticles(htmls['articles'])
            self.ProFile['articles']=arts
          if category =="videos":
            vids=self.getArticles(htmls['videos'])
            self.ProFile['articles']=vids
          return self.ProFile


class HarvestProduct:
    """
    A Content harvester for a single product page
    e.g. /specsearch/partspecs?partId={D83387DD-BB71-4963-8654-3EBB35598EAF}&vid=129159&comp=2940&sqid=19029003

    ProDuck = {
        'breadcrumb' : '' #
        'title'      : '' #
        'content'    : '' #html of the main content in <div id="inner-content>"
        'external'   :   '' #the "Get More Info on Supplier's Site" href
        'datasheet'  : '' 
        'product_image'  : '' #url of image
        'supplier'  : '' #supplier name from <div class="supplier-name">
        'videos'     :  [] #For later extraction from 'content'
        'images'     :  [] #For later extraction from 'content'
        'pdfs'       :  [] #For later extraction from 'content'
        'files'       : [] #Everything else, for later extraction from 'content'
    }
    """
    ProDuck={}

    def get(self,html):
        soup = bs(html,"html.parser")
        breadcrumb=soup.find( "div",attrs={"id":"breadcrumb"} )
        title = soup.find("div",attrs={"id":"header-container"}).find("h1").getText().strip()
        content = soup.find("div",attrs={"id":"inner-content"})
        external=content.find("a",attrs={"class","external"})['href']
        datasheet=content.find("div",attrs={"class","datasheet-button-container"}).find("a")["data-direct-link"]
        product_image=content.find("img",attrs={"id":"product-image", "class":"post-load"})["realsrc"]
        supplier = soup.find("div",attrs={"class":"supplier-name"}).getText().strip()

        return(
            {
                "breadcrumb": str(breadcrumb),
                "title"     : title,
                "content"   : str(content),
                "external"  : external,
                "datasheet" : datasheet,
                "product_image" : product_image,
                "supplier" : supplier,
                "videos"    : [],
                "images"    : [],
                "pdfs"      : [],
                "files"     : [],
            }
        )
