#File to hold update record scripts

from supabaseClient import supabase

def update_asset(asset_id,asset_details):
    current_details=supabase.table("devices").select('*').eq('id', asset_id).execute().data[0]
    if asset_details["hostname"]:
        response=supabase.table("devices").update({"hostname":asset_details["hostname"]}).eq('id', asset_id).execute()
    if int(asset_details["type_id"]) != current_details["type_id"]:
        response=supabase.table("devices").update({"type_id":int(asset_details["type_id"])}).eq('id', asset_id).execute()
    if int(asset_details["customer_id"]) != current_details["customer_id"]:
        response=supabase.table("devices").update({"customer_id":int(asset_details["customer_id"])}).eq('id', asset_id).execute()
    if int(asset_details["status_id"]) != current_details["status_id"]:
        response=supabase.table("devices").update({"status_id":int(asset_details["status_id"])}).eq('id', asset_id).execute()
    print(response)
    return response.data[0]

def update_customer(customer_id, customer_details):
    print("function running")
    print(customer_details)
    current_details=supabase.table("customers").select('*').eq('id', customer_id).execute().data[0]
    print(current_details)
    if customer_details["customer_name"]:
        response=supabase.table("customers").update({"customer_name":customer_details["customer_name"]}).eq('id', customer_id).execute()
    if int(customer_details["teir"]) != current_details["teir"]:
        response=supabase.table("customers").update({"teir":int(customer_details["teir"])}).eq('id', customer_id).execute()
    print(response)
    return None
