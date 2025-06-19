#File to hold create record scripts

from supabaseClient import supabase
from flask import session

def add_asset_to_database(asset_dict):
    response=supabase.table("devices").insert(asset_dict).execute()
    print(response.data)
    return response.data[0]

def add_customer_to_database(customer_dict):
    response=supabase.table("customers").insert(customer_dict).execute()
    print(response.data)
    return response.data[0]

def add_user_to_database(user_dict):
    response=supabase.table("users").insert(user_dict).execute()
    print(response.data)
    return response.data[0]

def create_request(request_dict):
    final_request=dict(request_dict)
    final_request["user_id"] = session["user_id"]
    final_request["status_id"] = 1
    if not final_request["device_id"]:
        final_request["device_id"] = None
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        final_request["customer_id"] = session["customer_id"]
    response=supabase.table("user_requests").insert(final_request).execute()
    print(response.data)
    return response.data[0]
