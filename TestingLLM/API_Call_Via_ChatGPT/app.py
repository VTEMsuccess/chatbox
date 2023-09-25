from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

class FDEnquiryModel(BaseModel):
    service_package: str
    tenor: int

class FDMaturityModel(BaseModel):
    customer_id: int
 
app = FastAPI()

@app.post("/fdenquiry/")
def fd_enquiry(fdenquirydata: FDEnquiryModel):
    df = pd.read_csv("fd_interest_rates.csv")
    service_package = fdenquirydata.service_package
    print("Service package: {}".format(service_package))
    tenor = fdenquirydata.tenor
    print("Tenor is: {}".format(tenor))
    row = df[(df['service_package'] == service_package) & (df['tenors_start'] <= tenor) & (df['tenor_end'] >= tenor)]
    if row.empty:
        return {
            "error_msg": "Invalid service package or tenor",
            "status": "ERROR"
        }
    price = row['price'].values[0]
    print("Price: {}".format(price))
    return {
        "service_package": service_package,
        "tenor": tenor,
        "price": price,
        "status": "SUCCESS"
    }

@app.post("/fdmaturity/")
def fd_maturity(fdmaturitydata: FDMaturityModel):
    df = pd.read_csv("fd_maturity.csv")
    customer_id = fdmaturitydata.customer_id
    print("Customer ID: {}".format(customer_id))
    row = df[df["customer_id"] == customer_id]
    if row.empty:
        return {
            "error_msg": "Customer ID does not exist",
            "status": "ERROR"
        }
    name = row['name'].values[0]
    package_purchased = row['package_purchased'].values[0]
    price = row['price'].values[0]
    return {
        "customer_id": customer_id,
        "name": name,
        "package_purchased": package_purchased,
        "price": price,
        "status": "SUCCESS"
    }
