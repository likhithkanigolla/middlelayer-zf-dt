import json
import requests
import time
from database import SessionLocal, ModelCoefficients, get_db, User
# from config.settings import *

# BACKEND_URL="http://onem2m.iiit.ac.in:443/~/in-cse/in-name/AE-DM/"
BACKEND_URL="http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/AE-CM/"

def post_to_onem2m(node_name, data, db, current_user):
    epoch_time = int(time.time())
    compensated_voltage=float(data['voltage'])
    temperature=float(data['temperature'])
    # compensated_voltage= voltage/(1.0+0.02*(temperature-25))
    
    query_results = db.query(ModelCoefficients).filter(ModelCoefficients.model_name == node_name).first()
    coefficients = query_results.coefficients.split(",")
    compensated_tds= (float(coefficients[0])*compensated_voltage**3)- (float(coefficients[1])*compensated_voltage**2) + (float(coefficients[2])*compensated_voltage*0.5)
    print(compensated_tds)
    data_list = [epoch_time,temperature,compensated_voltage,compensated_tds]  # Initialize the data list with some default values
    url = BACKEND_URL + node_name + "/Data"
    data_list=str(data_list)
    payload = json.dumps({
        "m2m:cin": {
            "con": data_list
        }
    })
    headers = {
        'X-M2M-Origin': 'Tue_20_12_22:Tue_20_12_22',
        'Content-Type': 'application/json;ty=4'
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.status_code
    # return coefficients
# print(DATABASE_URL)