import json
from harvesters.content import *
from harvesters.directory import Catalogs

from .fetch import Fetch,FetchCatalogs

def build_catalogs(catalogs):
    fet=fetch.Fetch()

    print("=============Fetch Catalogs======")
    for entry in catalogs:
        #print("entry: "+str(entry) )
        json=fet.http_get(entry['url'])
        #print("json: "+str(json));
        catalogs=Catalogs().get_catalogs(json)
        #c,p,e=FetchCatalogs()
        print(catalogs)







if __name__=="__main__":
    with open("../output/catalogs.json","r") as f:
        catalogs=json.load(f)
    build_catalogs(catalogs)





