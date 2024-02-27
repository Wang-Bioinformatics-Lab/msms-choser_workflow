import os
import csv
import requests
import urllib.parse

# this is used to query inchi, smiles using Ming's web api
def mass_from_inchi (inchi):
    url = "https://structure.gnps2.org/structuremass?inchi={}".format(urllib.parse.quote(inchi))
    response = requests.get(url)
    if response.status_code !=200 :
        print("no results")
        #print (response.text)
        print(url)
        return 0
    return float(response.text)

def mass_from_smiles (smiles):
    url = "https://structure.gnps2.org/structuremass?smiles={}".format(urllib.parse.quote(smiles))
    response = requests.get(url)
    if response.status_code !=200 :
        print("no results", response, url)
        return -1
    return float(response.text)
