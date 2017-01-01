import requests
from harvesters.directory import *
import json

letters=[chr(l) for l in range(ord('a'),ord('z')+1) ]
letters.append("1")


class Fetch():

    def load_cookies(self,cookies_string):
        lines=cookies_string.split(";")
        ret={}
        for line in lines:
            cookie_name=line.split("=")[0]
            cookie_value = line.split("=")[1]
            ret[cookie_name]=cookie_value
        print(ret)
        return ret

    def load_headers(self,fname):
        """
        Loads headers from a file
        """
        lines=open(fname,"r").readlines()
        ret_headers={}
        ret_cookies = {}
        for line in lines:
            n=line.split(": ")[0].strip()
            v=line.split(": ")[1].strip()
            if(n=="Cookie"):
                ret_cookies=self.load_cookies(v)
            else:
                ret_headers[n]=v
        return ret_headers,ret_cookies


    def http_get(self,url):
        print("Getting "+url);
        ses=requests.Session()
        headers,cookies=self.load_headers("../tmp/browser_headers.txt")

        #ses.headers=headers
        #ses.cookies=cookies
        #print(ses.cookies)

        resp=ses.get(url,cookies=cookies,allow_redirects=True)
        #print(resp)
        #print(resp.text)
        return resp.text

        #headers=self.load_headers("../tmp/browser_headers.txt")
        #headers['User-Agent']="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
        #session = requests.session()
        #resp = session.get(url,headers=headers,allow_redirects=True)
        #return resp.text

class DirectoryFetch(Fetch):
    def harvest(self,content):
        """To override in classes"""
        """
        This will define which harvesting function we're going to use
        """
        pass

    def test(self,content):
        """To override in classes"""
        """
        This will execute on the fetched directory page to check it's now empty (past last page)

        """
        pass

    #def pages_get(self, base_url, letter, start_page=1, end_page=999): #Production
    def pages_get(self,base_url,letter,start_page=30,end_page=35):
        ret=[]
        for page in range(start_page,end_page):
            url=base_url+letter+"/"+str(page)
            content=self.http_get(url)
            if self.test(content):
                buffer=self.harvest(content)
                ret.extend(buffer)
            else:
                return ret;

    def directory_get(self):
        ret = []
        # for letter in letters: #Production
        for letter in ['a']:
            buff = self.pages_get(self.base_url,letter)
            ret.extend(buff)
        return ret



class FetchProduct(Fetch):
    pass


class FetchIndustrialDirectory(DirectoryFetch):
    def __init__(self,base_url):
        self.base_url=base_url

    def test(self,content):
        if "<tr>" in content: return True
        else: return False

    def harvest(self,content):
        return Industrial().get(content)

    def fetch_industrial_directory(self):
        print("Fetch Industrial Directory")
        ret=self.directory_get()
        return ret


class FetchIndustrialCategory(DirectoryFetch):
    def __init__(self,industrial_directory_index_file):
        with open(industrial_directory_index_file,"r") as f:
            self.industrial_directories=json.load(f)

    def fetch_categories(self):
        ret=[]
        for entry in self.industrial_directories:
            print("Fetching category")
            content=self.http_get(entry['url'])
            buff=Categories().get(content)
            ret.extend(buff)
        return ret


class FetchCatalogs(Fetch):
    """
    Fetches catalogs and products from an industrial category or another catalog
    """
    catalog_url_format="http://www.globalspec.com/Search/GetProductResults?sqid=0&comp={0}&show=products&method=getNewResults"
    catalogs_index_file=""

    def __init__(self, catalogs_index_file):
        self.catalogs_index_file=catalogs_index_file
        with open(catalogs_index_file,"r") as f:
            self.catalogs=json.load(f)

    def save(self,catalogs,products,errors):
        print("Saving")
        with open("../output/catalogs.json", "w+") as f:
            json.dump(catalogs, f, sort_keys=True, indent=4)
        with open("../output/products.json", "w+") as f:
            json.dump(products, f, sort_keys=True, indent=4)
        with open("../output/errors.json", "w+") as f:
            json.dump(errors, f, sort_keys=True, indent=4)



    def harvest_catalog(self,catalog_url):
        """
        Harvest a catalog from a url
        :param catalog_url:
        :return: ret_catalogs,ret_products,ret_errors
        """
        ret_catalogs=[]
        ret_products=[]
        ret_errors=[]
        catalog_json_obj=self.http_get(catalog_url)
        catalogs=Catalogs().get_catalogs(catalog_json_obj)
        products = Catalogs().get_products(catalog_json_obj)
        ret_catalogs.extend(catalogs)
        ret_products.extend(products)
        for catalog in catalogs:
            if catalog not in ret_catalogs and catalog['harvested']==False:
                c,p,e=self.harvest_catalog(catalog['uri'])
                ret_catalogs.extend(c)
                ret_products.extend(p)
                ret_errors.extend(e)
                catalog['harvested']=True
        print("---------------------------------")
        print("Catalogs: "+str(catalogs) )
        print("Products: "+str(products) )
        #print(catalog_json_obj)
        return ret_catalogs,ret_products,ret_errors



    def build_catalogs_indices(self):
        #Builds the catalog and products index from industrial_categories.json


        ret_catalogs=[] #A list of catalogs to harvest
        ret_products=[] #A list of products to harvest
        ret_errors=[]
        idx=0
        for entry in self.catalogs:
            if entry['harvested']==True:
                print("Already harvested "+entry['url'])
                continue
            url=entry['url']
            category_id=entry['category_id']
            if category_id is not None: # Catalog
                url=self.catalog_url_format.format(category_id)
                print("Cataloge: " + category_id + " - " + url)
                entry['url'] = url
                ret_catalogs.append(entry)
                c,p,e=self.harvest_catalog(url)
                ret_catalogs.extend(c)
                ret_products.extend(p)
                ret_errors.extend(e)
                #entry['harvested'] = True

            else: #Product
                try:
                    print("Product: "+url)
                    ret_products.append(entry)
                    #entry['harvested'] = True
                except:
                    print("Error")
                    ret_errors.append(entry)
            idx+=1
            if idx%100 == 0 : #Save every 100 records
                self.save(ret_catalogs,ret_products,ret_errors)
                with open(self.catalogs_index_file,"w") as f:
                    json.dump(self.catalogs,f, sort_keys=True, indent=4)

        return ret_catalogs,ret_products,ret_errors


class FetchSuppliers(DirectoryFetch):
    def __init__(self,base_url):
        self.base_url=base_url

    def test(self,content):
        if "Unknown or Obsolete Product Category Reference" in content:
            return False
        else:
            return True

    def harvest(self,content):
        data=Suppliers().get(content)
        return data


    def fetch_suppliers(self):
        print("Fetch Suppliers");
        ret=self.directory_get()
        return ret


if __name__=='__main__':
    suppliers_url = "http://www.globalspec.com/SpecSearch/SuppliersByName/AllSuppliers/"
    industrial_url= "http://www.globalspec.com/industrial-directory/browse/"

    #suppliers=FetchSuppliers(suppliers_url)
    #all_suppliers=suppliers.fetch_suppliers()
    #with open("../output/suppliers_directory.json","w+") as f:
    #    json.dump(all_suppliers,f, sort_keys=True, indent=4)


    #industrial_directory=FetchIndustrialDirectory(industrial_url)
    #all_industrial_directory=industrial_directory.fetch_industrial_directory()
    #with open("../output/industrial_directory.json","w+") as f:
    #    json.dump(all_industrial_directory,f, sort_keys=True, indent=4)


    #industrial_categories=FetchIndustrialCategory("../output/industrial_directory.json")
    #all_categories=industrial_categories.fetch_categories()
    #with open("../output/industrial_categories.json","w+") as f:
    #    json.dump(all_categories,f, sort_keys=True, indent=4)


    #Get catalogs and products indices from index we got from industrial directory
    """
    catalogs=FetchCatalogs("../output/industrial_categories.json")
    all_catalogs,all_products,all_errors=catalogs.build_catalogs_indices();

    with open("../output/catalogs.json","w+") as f:
        json.dump(all_catalogs,f, sort_keys=True, indent=4)
    with open("../output/products.json","w+") as f:
        json.dump(all_products,f, sort_keys=True, indent=4)
    with open("../output/errors.json","w+") as f:
        json.dump(all_errors,f, sort_keys=True, indent=4)
    """






    """
    #Tests fetching a page
    #u="http://datasheets.globalspec.com/ds/4365/PHOTONIS"
    u="http://www.globalspec.com/specsearch/partspecs?partId={4A28D11F-7813-4B8C-9ACF-5B97B9104657}&vid=178302&comp=4365"

    fet=Fetch()
    html=fet.http_get(u)
    print(html)
    record=HarvestProduct().get(html)
    print(record)
    """