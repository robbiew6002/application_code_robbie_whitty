#This is the main application file that sets up the Flask app and routes.

from flask import Flask, session, redirect, url_for, request, render_template
from supabaseClient import supabase
from auth import check_credentials
from search import search_assets, search_customers, return_asset_by_id, return_customer_by_id
from create import add_asset_to_database, add_customer_to_database
from update import update_asset, update_customer
app = Flask(__name__)
app.secret_key='56ca809dc0b69a58c4d278ee41b44da5ea645163ec7d3a0ab9a1c37f63aec318d0f775ce8a11e5e336ac6023132bdf242453ed1bb12c8bfac6584f2c77d3d04de8a4149eb29b5f93a8042a397b0143623b3097a6a0d6fe8b0e94fd41f6b9c61d323e82cdcea7c7ddca9eb3460acfa1bc34fa3fd09bd82758a6201172a8479925c2518e014d03230ac75c3889adafae1f43245ceb8aefa488966611066d14854bb1b1cf492fd345b20e533e63688f6ab0c442f104557b1d299981a6a7f9ca3e08985c5623c340147e7ba9cfbb8310ce9ced434c2a4b49d781cbbfe1a7d9ddaea83bb24b5c73cdef0a8773cf2a6265bad46fab6d6ecfa0992dc2fd70b887f32267'

@app.route("/")
def index():
    if not session.get('logged_in'):
        return render_template("login.html")
    else:
        return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def do_admin_login():
    if not session.get('logged_in'):
        check_credentials(request.form)
    if session.get('logged_in'):
        return redirect(url_for('home'))
    return redirect(url_for('index'))

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    else:
        print("session:", session)
        return render_template("home.html")

@app.route('/logout')
def logout():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    session.clear()
    return redirect(url_for('index'))

@app.route('/assets')
def display_assets():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #Move to search file#
    if session['auth_level'] == 1 or session['auth_level'] == 2:
        response = supabase.table("devices").select("id, hostname, device_types(name), statuses(value), customers(customer_name)" ).execute()
    else:
        response = supabase.table("devices").select("id, hostname, device_types(name), statuses(value)").eq("customer_id", session['customer_id']).execute()
    assets = response.data
    # ^^ #
    return render_template("assets.html", assets=assets)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if not session.get('logged_in'):
            return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template("search.html")
    if request.method=='POST':
        return render_template("search.html", results=search_assets(request.form))

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if not session.get('logged_in') or (session['auth_level'] != 2 and session['auth_level'] != 1):
            return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template("customers.html")
    if request.method=='POST':
        return render_template("customers.html", results=search_customers(request.form))

@app.route('/create')
def create():
    if not session.get('logged_in') or (session['auth_level'] != 2 and session['auth_level'] != 1):
        return redirect(url_for('index'))
    return render_template("create.html", customers=supabase.table("customers").select("id","customer_name").execute().data,
                        device_types=supabase.table("device_types").select("id", "name").execute().data,
                        statuses=supabase.table("statuses").select("id","value").execute().data)

@app.route('/create/asset', methods=['POST'])
def create_asset():
    if not session.get('logged_in') or (session['auth_level'] != 2 and session['auth_level'] != 1):
        return redirect(url_for('index'))
    new_asset=add_asset_to_database(request.form)
    return render_template("create.html", customers=supabase.table("customers").select("id", "customer_name").execute().data,
                        device_types=supabase.table("device_types").select("id", "name").execute().data,
                        statuses=supabase.table("statuses").select("id", "value").execute().data, asset_created=new_asset)

@app.route('/create/customer', methods=['POST'])
def create_customer():
    if not session.get('logged_in') or (session['auth_level'] != 2 and session['auth_level'] != 1):
        return redirect(url_for('index'))
    new_customer=add_customer_to_database(request.form)
    return render_template("create.html", customers=supabase.table("customers").select("id", "customer_name").execute().data,
                        device_types=supabase.table("device_types").select("id", "name").execute().data,
                        statuses=supabase.table("statuses").select("id", "value").execute().data, customer_created=new_customer)

@app.route('/assets/<asset_id>', methods=['GET', 'POST'])
def single_asset(asset_id):
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    if (session['auth_level'] != 2 and session['auth_level'] != 1):
        return redirect(url_for('display_assets'))
    asset_details=return_asset_by_id(asset_id)
    if request.method == 'GET':
        if not asset_details:
            return redirect(url_for('display_assets'))
        return render_template("single_asset.html", asset=asset_details,
            device_types=supabase.table("device_types").select("id", "name").execute().data,
            statuses=supabase.table("statuses").select("id", "value").execute().data,
            customers=supabase.table("customers").select("id", "customer_name").execute().data)
    if request.method == 'POST':
        asset_details=update_asset(asset_details["id"], request.form)
        return redirect(f"/assets/{asset_id}")

@app.route('/customers/<customer_id>', methods=['GET', 'POST'])
def single_customer(customer_id):
    if not session.get('logged_in') or (session['auth_level'] != 2 and session['auth_level'] != 1):
        return redirect(url_for('index'))
    customer_details=return_customer_by_id(customer_id)
    if request.method == 'GET':
        if not customer_details:
            return redirect(url_for('customers'))
        print(customer_details)
        return render_template("single_customer.html", customer=customer_details)
    if request.method == 'POST':
        print(request.form)
        customer_details=update_customer(customer_details["id"], request.form)
        return redirect(f"/customers/{customer_id}")