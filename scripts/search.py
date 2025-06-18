from supabaseClient import supabase
from flask import session

def return_status_id(status_value):
    response = supabase.table("statuses").select("id").eq("value", status_value).execute()
    if response.data:
        print("Status ID:", response.data[0]['id'])
        return response.data[0]['id']
    else:
        return None

def return_device_type_id(type_value):
    response = supabase.table("device_types").select("id").eq("name", type_value).execute()
    if response.data:
        print("Device Type ID:", response.data[0]['id'])
        return response.data[0]['id']
    else:
        return None

def return_customer_id(customer_name):
    response = supabase.table("customers").select("id").eq("customer_name", customer_name).execute()
    if response.data:
        print("Customer ID:", response.data[0]['id'])
        return response.data[0]['id']
    else:
        return None

def search_assets(search_dict):
    search_dict = dict(search_dict)
    search_array = []
    for item in search_dict:
        if search_dict[item]:
            search_array.append(item)
    if session["auth_level"] == 1 or session["auth_level"] == 2:
        if len(search_array) == 0:
            asset_response = supabase.table("devices").select("*, device_types(name), statuses(value), customers(customer_name)").execute()
        if len(search_array) == 1:
            asset_response = supabase.table("devices").select("*, device_types(name), statuses(value), customers(customer_name)").eq(search_array[0], search_dict[search_array[0]]).execute()
        if len(search_array) == 2:
            asset_response = supabase.table("devices").select("*, device_types(name), statuses(value), customers(customer_name)").eq(search_array[0], search_dict[search_array[0]]).eq(search_array[1], search_dict[search_array[1]]).execute()
        if len(search_array) == 3:
            asset_response = supabase.table("devices").select("*, device_types(name), statuses(value), customers(customer_name)").eq(search_array[0], search_dict[search_array[0]]).eq(search_array[1], search_dict[search_array[1]]).eq(search_array[2], search_dict[search_array[2]]).execute()
        if len(search_array) == 4:
            asset_response = supabase.table("devices").select("*, device_types(name), statuses(value), customers(customer_name)").eq(search_array[0], search_dict[search_array[0]]).eq(search_array[1], search_dict[search_array[1]]).eq(search_array[2], search_dict[search_array[2]]).eq(search_array[1], search_dict[search_array[3]]).execute()
    else: 
        if len(search_array) == 0:
            asset_response = supabase.table("devices").select("*, device_types(name), statuses(value)").eq("customer_id", session["customer_id"]).execute()
        if len(search_array) == 1:
            asset_response = supabase.table("devices").select("*, device_types(name), statuses(value)").eq(search_array[0], search_dict[search_array[0]]).eq("customer_id", session["customer_id"]).execute()
        if len(search_array) == 2:
            asset_response = supabase.table("devices").select("*, device_types(name), statuses(value)").eq(search_array[0], search_dict[search_array[0]]).eq(search_array[1], search_dict[search_array[1]]).eq("customer_id", session["customer_id"]).execute()
        if len(search_array) == 3:
            asset_response = supabase.table("devices").select("*, device_types(name), statuses(value)").eq(search_array[0], search_dict[search_array[0]]).eq(search_array[1], search_dict[search_array[1]]).eq(search_array[2], search_dict[search_array[2]]).eq("customer_id", session["customer_id"]).execute()
    return asset_response.data if asset_response.data else None

#def search_assets(search_dict):
    #search_dict=dict(search_dict)
    #if search_dict['status_id']:
    #    search_dict['status_id'] = return_status_id(search_dict['status_id'])
    #if search_dict['type_id']:
    #    search_dict['type_id'] = return_device_type_id(search_dict['type_id'])
    #if session['auth_level'] == 1 or session['auth_level'] == 2:
    #    if search_dict['customer_id'] :
    #        search_dict['customer_id'] = return_customer_id(search_dict['customer_id'])
    #elif session['auth_level'] != 1 and session['auth_level'] != 2:
    #    search_dict['customer_id'] = session['customer_id']
    #search_array=[]
    #print("Search Dictionary:", search_dict)
    #for item in search_dict:
    #    if search_dict[item]:
    #        search_array.append(item)
    #if len(search_array) == 0:
    #    return []
    #if len(search_array) == 1:
    #    response = supabase.table("devices").select("hostname, device_types(name), statuses(value), customers(customer_name)").eq(search_array[0], search_dict[search_array[0]]).execute()
    #    print(response)
    #if len(search_array) == 2:
    #    response = supabase.table("devices").select("hostname, device_types(name), statuses(value), customers(customer_name)").eq(search_array[0], search_dict[search_array[0]]).eq(search_array[1], search_dict[search_array[1]]).execute()
    #    print(response)
    #if len(search_array) == 3:
    #    response = supabase.table("devices").select("hostname, device_types(name), statuses(value), customers(customer_name)").eq(search_array[0], search_dict[search_array[0]]).eq(search_array[1], search_dict[search_array[1]]).eq(search_array[2], search_dict[search_array[2]]).execute()
    #    print(response)
    #return response.data if response.data else None


def search_customers(search_dict):
    search_dict = dict(search_dict)
    search_array = []
    for item in search_dict:
        if search_dict[item]:
            search_array.append(item)
    if len(search_array) == 0:
        customer_response = supabase.table("customers").select("*").execute()
    if len(search_array) == 1:
        customer_response = supabase.table("customers").select("*").eq(search_array[0], search_dict[search_array[0]]).execute()
    if len(search_array) == 2:
        customer_response = supabase.table("customers").select("*").eq(search_array[0], search_dict[search_array[0]]).eq(search_array[1], search_dict[search_array[1]]).execute()
    if customer_response.data is None:
        return None
    for customer in customer_response.data:
        customer['device_count'] = supabase.table("devices").select("id", count="exact").eq("customer_id", customer['id']).execute().count
    return customer_response.data

def return_asset_by_id(asset_id):
    asset_details=supabase.table("devices").select('*, device_types(name), statuses(value), customers(customer_name)').eq('id', asset_id).execute()
    if len(asset_details.data) > 0:
        return asset_details.data[0]
    return None

def return_customer_by_id(customer_id):
    customer_details=supabase.table("customers").select('*').eq('id', customer_id).execute()
    if len(customer_details.data) > 0:
        return customer_details.data[0]
    return None

def return_users(search_dict):
    if search_dict == None:
        users=supabase.table("users").select('*, customers(customer_name)').execute().data
        return users
    else:
        search_dict = dict(search_dict)
        if search_dict["customer"]:
            customer_results=supabase.table("customers").select("id").eq("customer_name",search_dict["customer"]).execute().data
            if len(customer_results) > 0:
                search_dict["customer_id"]=customer_results[0]["id"]
                search_dict.pop("customer")
            else:
                return None
        search_array = []
        for item in search_dict:
            if search_dict[item]:
                search_array.append(item)
        if len(search_array) == 0:
            user_response = supabase.table("users").select("*,customers(customer_name)").execute()
        if len(search_array) == 1:
            user_response = supabase.table("users").select("*,customers(customer_name)").eq(search_array[0], search_dict[search_array[0]]).execute()
        if len(search_array) == 2:
            user_response = supabase.table("users").select("*,customers(customer_name)").eq(search_array[0], search_dict[search_array[0]]).eq(search_array[1], search_dict[search_array[1]]).execute()
        if user_response.data is None:
            return None
        return user_response.data

def return_user_by_id(user_id):
    user_details=supabase.table("users").select("*,customers(customer_name)").eq('id', user_id).execute()
    if len(user_details.data) > 0:
        return user_details.data[0]
    return None