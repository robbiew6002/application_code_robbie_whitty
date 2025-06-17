from supabaseClient import supabase

def delete_asset_by_id (asset_id):
    response = supabase.table("devices").delete().eq("id", asset_id).execute()

def delete_customer_by_id(customer_id):
    response = supabase.table("customers").delete().eq("id", customer_id).execute()
