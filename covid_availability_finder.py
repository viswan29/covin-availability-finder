import json
import datetime
import requests
import pandas as pd
from cachetools import cached,TTLCache

def get_districts():
        
    all_districts = None
    for i in range(1,40):
        response = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}".format(i), timeout=3)
        districts_df=pd.DataFrame(json.loads(response.text))
        districts_df=pd.json_normalize(districts_df['districts'])
        if all_districts is None:
            all_districts=districts_df
        else:
            all_districts=pd.concat([all_districts,districts_df])
        all_districts['district_id'] = all_districts['district_id'].astype(int)
        all_districts = all_districts.sort_values("district_name")
        
    return all_districts

@cached(cache=TTLCache(maxsize=1024,ttl=600))
def get_data(url):
    response=requests.get(url,timeout=3)
    data=json.loads(response.text)['centers']
    return data

def get_availability(district_ids,min_age_limit):
    curdate=datetime.datetime.today().strftime("%d-%m-%Y")
    full_df = None
    for district_id in district_ids:
        url="https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(district_id, curdate)
        data = get_data(url)
        df=pd.DataFrame(data)
        if df is not None:
            df=df.explode('sessions')
            df['min_age_limit']=df.sessions.apply(lambda x: x['min_age_limit'])
            df['available_capacity'] = df.sessions.apply(lambda x: x['available_capacity'])
            df['date'] = df.sessions.apply(lambda x: x['date'])
            df=df[["date", "min_age_limit", "available_capacity", "pincode", "name", "state_name", "district_name", "fee_type"]]
            if full_df is not None:
                full_df = pd.concat([full_df,df])
            else:
                full_df=df
    
    if full_df is not None:
        full_df = full_df.sort_values(["min_age_limit","date"], ascending=[True, True])
        full_df = full_df[full_df['min_age_limit'] >= min_age_limit]
        full_df = full_df[full_df['available_capacity']>0]
        full_df.set_index('date', inplace=True)
        return full_df
    return pd.DataFrame()

        
if __name__ == "__main__":
    Ahmedabad = 154
    Ahmedabad_Corporation = 770
    dist_ids = [Ahmedabad, Ahmedabad_Corporation]
    min_age_limit = 18
    availability_data = get_availability(dist_ids, min_age_limit)
