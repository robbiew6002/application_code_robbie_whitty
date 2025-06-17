#File to hold create record scripts

from supabaseClient import supabase

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
