from lexnlp.extract.en.addresses import addresses
import nltk
import sklearn
import lexnlp
import fitz
import pandas as pd
import numpy as numpy
import os
import re
from .data_classes import Address

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')



from geopy.geocoders import Nominatim

# Initialize the Nominatim geocoder
geolocator = Nominatim(user_agent="geoapiExercises")

def get_country_from_string(location_string):
    try:
        # Use geopy to perform geocoding and get location information
        location = geolocator.geocode(location_string)
        
        if location:
            # Extract the country name
            country = location.address.split(",")[-1]
            return country.strip()
        else:
            return None
    except Exception as e:
        print("Error:", str(e))
        return None
    

def combine_bbox_along_y(bbox_list, distance_threshold=10):
    combined_words = []

    i = 0
    while i < len(bbox_list):
        curr_bbox = bbox_list[i]
        combined_text = curr_bbox[4]
        x1, y1, x2, y2 = curr_bbox[:4]

        j = i + 1
        while j < len(bbox_list):
            next_bbox = bbox_list[j]
            next_x1, next_y1, _, _ = next_bbox[:4]

            if (abs(next_y1 - y2) <= distance_threshold  and abs(next_x1-x1)<=30):
                combined_text += "\n" + next_bbox[4]
                x2 = next_bbox[2]
                j += 1
            else:
                break

        combined_words.append((x1, y1, x2, y2, combined_text))
        i = j

    return combined_words

def has_matching_pattern(text,pattern):
    
    matches = re.findall(pattern, text, re.MULTILINE)
    return bool(matches)


def address_extraction(file_path): 
    addresses_list=[]
    doc = fitz.open(file_path)

    for page_no in range(len(doc)):
        page=doc[page_no]

        blocks= page.get_text('blocks')


        blocks = combine_bbox_along_y(blocks, 8)
        blocks = sorted(blocks ,key = lambda x :x[1])

        for block in blocks:

            us_pattern= r"\d+?[\s]+?[a-zA-Z0-9\s]+,?([a-zA-Z\s]+,?)?[\s]+?([A-Z]{2})?[\s]?[0-9]{5,6}"
            france_pattern=r"[A-Z][A-Za-zàâçéèêëîïôûùüÿñæœ\s]+?,?[\s]+?\d+?,?[\s]+?[A-Za-zàâçéèêëîïôûùüÿñæœ\s]+[\s]+?(\d{5})[\s]+?[A-Za-z0-9\s]+?[\s]+?[\d]+?[\s]+?"
            singapore_pattern=r"(\d+?[\s]?[A-Z][A-Za-z0-9\s]+)?,?[\s]+([#|No]?[0-9\-?]+?)?,?[\s][A-Z][A-Za-z\s]+,?[\s]?[Singapore]?\d{6}"
            uk_pattern=r"[A-Z]([A-za-a\s]+)?,?[\s]+?[0-9]+?[\s]+?[A-za-a\s]+?,?[\s]+?[A-Za-z0-9]{2,5}[\s\-][A-Za-z0-9]{2,5}"
            matches = re.findall(us_pattern, block[4], re.MULTILINE)
            if len(matches)>0:
                possible_addresses=list(addresses.get_address_spans(str(block[4])))
                # print(possible_addresses)
                if len(possible_addresses)>0:
                    address=Address(text=block[4],bbox=block[0:4])
                    addresses_list.append(address)
                    

                
            
        # break  
    return addresses_list
        


