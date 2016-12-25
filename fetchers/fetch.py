import requests
from harvesters.directory import *
from harvesters.content import *
import json

letters=[chr(l) for l in range(ord('a'),ord('z')+1) ]
letters.append("1")

class Fetch():
    def load_headers(self,fname):
        """
        Loads headers from a file
        """
        lines=open(fname,"r").readlines()
        ret={}
        for line in lines:
            n=line.split(": ")[0].strip()
            v=line.split(": ")[1].strip()
            ret[n]=v
        return ret


    def http_get(self,url):
        headers=self.load_headers("../tmp/ff_headers.txt")
        session = requests.session()
        resp = session.get(url,headers=headers,allow_redirects=True)
        return resp.text

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

    def __init__(self, catalogs_index_file):
        with open(catalogs_index_file,"r") as f:
            self.catalogs=json.load(f)

    def fetch_catalogs(self):
        ret_catalogs=[]
        ret_products=[]
        ret_errors=[]
        for entry in self.catalogs:
            url=entry['url']
            category_id=entry['category_id']
            if category_id is not None: # Catalog
                url=self.catalog_url_format.format(category_id)
                print("Cataloge: " + category_id + " - " + url)
                entry['url'] = url
                ret_catalogs.append(entry)

            else: #Product
                try:
                    print("Product: "+url)
                    content=self.http_get(url)
                    buff=HarvestProduct.get(content)
                    ret_products.extend(buff)
                except:
                    print("Error with "+url)
                    ret_errors.append(entry)
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


    catalogs=FetchCatalogs("../output/industrial_categories.json")
    all_catalogs,all_products,all_errors=catalogs.fetch_catalogs();
    with open("../output/catalogs.json","w+") as f:
        json.dump(all_catalogs,f, sort_keys=True, indent=4)
    with open("../output/products.json","w+") as f:
        json.dump(all_products,f, sort_keys=True, indent=4)
    with open("../output/errors.json","w+") as f:
        json.dump(all_errors,f, sort_keys=True, indent=4)

