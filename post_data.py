import json
import requests
import time
from database import SessionLocal, ModelCoefficients, get_db, User
# from config.settings import *

BACKEND_URL="http://onem2m.iiit.ac.in:443/~/in-cse/in-name/"
# BACKEND_URL="http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/"

def post_to_onem2m_w1(node_name, data, db, current_user):
    epoch_time = int(time.time())
    voltage=float(data['voltage'])
    temperature=float(data['temperature'])
    compensated_voltage= voltage/(1.0+0.02*(temperature-25))
    
    query_results = db.query(ModelCoefficients).filter(ModelCoefficients.model_name == node_name).first()
    coefficients = query_results.coefficients.split(",")
    uncompensated_tds=(float(coefficients[0])*voltage**3)- (float(coefficients[1])*voltage**2) + (float(coefficients[2])*voltage*0.5)
    compensated_tds= (float(coefficients[0])*compensated_voltage**3)- (float(coefficients[1])*compensated_voltage**2) + (float(coefficients[2])*compensated_voltage*0.5)
    # print(compensated_tds)
    data_list = [epoch_time,temperature,voltage,uncompensated_tds,compensated_tds]
    url = BACKEND_URL + "AE-WM/WM-WD/" + node_name + "/Data"
    data_list=str(data_list)
    with open('./node-versions.json') as f:
        versions = json.load(f)
    version = versions.get(node_name, "Unknown")
    payload = json.dumps({
        "m2m:cin": {
            "lbl": ["AE-WM-WD", node_name, version, "WM-WD-" + version],
            "con": data_list
        }
    })
    headers = {
        'X-M2M-Origin': 'wdmon@20:gpod@llk4',
        'Content-Type': 'application/json;ty=4'
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.status_code

def post_to_onem2m_w2(node_name, data, db, current_user):
    epoch_time = int(time.time())
    voltage=float(data['voltage'])
    temperature=float(data['temperature'])
    ph=float(data['ph'])
    turbudity=float(data['turbidity'])
    compensated_voltage= voltage/(1.0+0.02*(temperature-25))
    
    query_results = db.query(ModelCoefficients).filter(ModelCoefficients.model_name == node_name).first()
    coefficients = query_results.coefficients.split(",")
    
    uncompensated_tds=(float(coefficients[0])*voltage**3)- (float(coefficients[1])*voltage**2) + (float(coefficients[2])*voltage*0.5)
    compensated_tds= (float(coefficients[0])*compensated_voltage**3)- (float(coefficients[1])*compensated_voltage**2) + (float(coefficients[2])*compensated_voltage*0.5)
    data_list = [epoch_time,temperature,voltage,uncompensated_tds,compensated_tds,turbudity,ph]  # Initialize the data list with some default values
    url = BACKEND_URL + "AE-WM/WM-WD/" + node_name + "/Data"
    data_list=str(data_list)
    with open('./node-versions.json') as f:
        versions = json.load(f)
    version = versions.get(node_name, "Unknown")
    payload = json.dumps({
        "m2m:cin": {
            "lbl": ["AE-WM-WD", node_name, version, "WM-WD-" + version],
            "con": data_list
        }
    })
    headers = {
        'X-M2M-Origin': 'wdmon@20:gpod@llk4',
        'Content-Type': 'application/json;ty=4'
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.status_code