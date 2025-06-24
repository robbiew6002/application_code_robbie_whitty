#This is the main application file that sets up the Flask app and routes.

# Module Imports - Imports the modules used to run the application.
# The below modules are installed via pip and are pre-made packages.
import sys
sys.path.append('./scripts')
from flask import Flask, session, redirect, url_for, request, render_template
from supabaseClient import supabase

# The below modules are files created within this application to implement modularity into the code.
from auth import check_credentials
from search import search_assets, search_customers, return_asset_by_id, return_customer_by_id, return_users, return_user_by_id, return_all_tickets, search_for_tickets, get_ticket_by_id, get_ticket_notes
from create import add_asset_to_database, add_customer_to_database, add_user_to_database, create_request, add_note_to_ticket, post_error_form
from update import update_asset, update_customer, update_user, change_ticket_device, change_ticket_customer, change_ticket_user, change_ticket_status, reassign_ticket_user
from delete import delete_asset_by_id, delete_customer_by_id, delete_user_by_id, delete_ticket_by_id, delete_note_by_id

# Set up new flask app. The application is provided a name equal to the primary file (index). The application is then passed a 
# secret key from the environment variables set in the terminal running the application
app = Flask(__name__)
app.secret_key='56ca809dc0b69a58c4d278ee41b44da5ea645163ec7d3a0ab9a1c37f63aec318d0f775ce8a11e5e336ac6023132bdf242453ed1bb12c8bfac6584f2c77d3d04de8a4149eb29b5f93a8042a397b0143623b3097a6a0d6fe8b0e94fd41f6b9c61d323e82cdcea7c7ddca9eb3460acfa1bc34fa3fd09bd82758a6201172a8479925c2518e014d03230ac75c3889adafae1f43245ceb8aefa488966611066d14854bb1b1cf492fd345b20e533e63688f6ab0c442f104557b1d299981a6a7f9ca3e08985c5623c340147e7ba9cfbb8310ce9ced434c2a4b49d781cbbfe1a7d9ddaea83bb24b5c73cdef0a8773cf2a6265bad46fab6d6ecfa0992dc2fd70b887f32267'

# The following establishes routes for the application. Each @app.route is provided a url endpoint on which to serve its function.
# All have a condition that will redirect the user to login if their session is not authenticated.

# Base route - This will render the login page if the user is not logged in (prompting them to login). If the user is logged in, 
# then they are forwarded to home.
@app.route("/")
def index():
    if not session.get('logged_in'):
        return render_template("login.html")
    else:
        return redirect(url_for('home'))

# Login Route - This route is for posting the login form. It only takes post requests. If the user is already logged in, then
# they are forwarded to the home page. If not logged in, then it takes the submitted login form and calls a function to check
# the provied credentials (function is from the auth module). If valid, the user is forwarded to the home page, if not, then they
# are redirected to the base url (prompting them to login again).
@app.route('/login', methods=['POST'])
def user_login():
    if not session.get('logged_in'):
        check_credentials(request.form)
    if session.get('logged_in'):
        return redirect(url_for('home'))
    return redirect(url_for('index'))

# Home Route - This route simply renders the application home page.
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    else:
        active_tickets=search_for_tickets({"status_id": 1, "user_id":""})
        print(active_tickets)
        return render_template("home.html", session_details=session, tickets=active_tickets)

# Logout route - If the user decides to logout, it clears their session and forwards them to the base route.
@app.route('/logout')
def logout():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    session.clear()
    return redirect(url_for('index'))

# Assets Route - This renders a page to display all assets the customer is authorised to view. The viewable assets are
# dependant on the users associated auth_level. Those with 1 or 2 can see all assets. Those with a different auth level
# can only see the ones linked to their customer. Additionally, more information about the assets is shown to the higher
# auth users. The post method is used to operate a filter form, searching for assets within the entire list. On initial
# load, all viewable assets are present, but the form can be used to filter this list. 
@app.route('/assets', methods=['GET', 'POST'])
def assets():
    if not session.get('logged_in'):
            return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template("assets.html", results=search_assets({}),
                                customers=supabase.table("customers").select("id","customer_name").execute().data,
                                device_types=supabase.table("device_types").select("id", "name").execute().data,
                                statuses=supabase.table("statuses").select("id","value").execute().data)
    if request.method=='POST':
        return render_template("assets.html", results=search_assets(request.form),
                                customers=supabase.table("customers").select("id","customer_name").execute().data,
                                device_types=supabase.table("device_types").select("id", "name").execute().data,
                                statuses=supabase.table("statuses").select("id","value").execute().data)

# Single Asset Route - This route is used to display information regarding a single asset. It is only viewable to users
# with an auth level of 1 or 2. A post request can be used to operate a form to change the assets details, updating them
# in the database. This post request calls a function from the update module to change the assets details before re-rendering
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
        update_asset(asset_details["id"], request.form)
        return redirect(f"/assets/{asset_id}")

# Delete Asset Route - This route is used to delete an asset from the database. It is only usable by a user with
# 1 or 2 authorisation. The route only operates on a post request before deleting the asset using a function 
# from the delete module. Once the file is deleted, the user is redirected to the all assets route. 
@app.route('/assets/<asset_id>/delete', methods=['POST'])
def delete_asset(asset_id):
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    if (session['auth_level'] != 2 and session['auth_level'] != 1):
        return redirect(url_for('display_assets'))
    if request.form:
        delete_asset_by_id(asset_id)
        return (redirect('/assets'))
    return (redirect(f'/assets/{asset_id}'))

# Cutomers Route - This route is used to display all customers registered on the system. It is only usable
# by 1 or 2 auth users. On initial load it displays all customrs, and then has a post method that calls a 
# function from the search module to filter the customer list displayed. 
@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if not session.get('logged_in') or (session['auth_level'] != 2 and session['auth_level'] != 1):
            return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template("customers.html", results = search_customers({}))
    if request.method=='POST':
        return render_template("customers.html", results=search_customers(request.form))

# Single Customer Route - This route displays a page for a single customer. It is only accessible to users
# with 1 or 2 auth. A form is used to opearate a function from the update module to alter a customers details
# via a post request. 
@app.route('/customers/<customer_id>', methods=['GET', 'POST'])
def single_customer(customer_id):
    if not session.get('logged_in') or (session['auth_level'] != 2 and session['auth_level'] != 1):
        return redirect(url_for('index'))
    customer_details=return_customer_by_id(customer_id)
    if request.method == 'GET':
        if not customer_details:
            return redirect(url_for('customers'))
        print(customer_details)
        return render_template("single_customer.html", customer=customer_details,
                                assets=supabase.table("devices").select("*, statuses(value), device_types(name)").eq("customer_id", customer_id).execute().data,
                                tickets=supabase.table("user_requests").select("*, request_statuses(Value), devices(hostname)").eq("customer_id", customer_id).or_("status_id.eq.1,status_id.eq.2").execute().data)
    if request.method == 'POST':
        print(request.form)
        update_customer(customer_details["id"], request.form)
        return redirect(f"/customers/{customer_id}")

# Delete Customer Route - This route is used to delete an customer from the database. It is only usable by a user with
# 1 or 2 authorisation. The route only operates on a post request before deleting the customer using a function 
# from the delete module. Once the file is deleted, the user is redirected to the all customers route. 
@app.route('/customers/<customer_id>/delete', methods=['POST'])
def delete_customer(customer_id):
    if not session.get('logged_in') or (session["auth_level"] != 1 and session["auth_level"] != 2):
        return redirect(url_for('index'))
    print(request.form)
    if request.form:
        delete_customer_by_id(customer_id)
        return (redirect('/customers'))
    return (redirect(f'/customers/{customer_id}'))

# Create Page Route - This renders a page with two html forms, one for creating a new customer and one for creating
# a new asset. The differnet forms will send a post request to a different endpoint. All create routes are only accessible to
# 1 or 2 auth users. 
@app.route('/create')
def create():
    if not session.get('logged_in') or (session['auth_level'] != 2 and session['auth_level'] != 1):
        return redirect(url_for('index'))
    return render_template("create.html", customers=supabase.table("customers").select("id","customer_name").execute().data,
                        device_types=supabase.table("device_types").select("id", "name").execute().data,
                        statuses=supabase.table("statuses").select("id","value").execute().data)

# Create Asset Function - This route is used for a post request to create a new asset. A function is called from the create
# module to create a new asset within the database. Once created, the user is redirected to the single asset page for the 
# new asset.
@app.route('/create/asset', methods=['POST'])
def create_asset():
    if not session.get('logged_in') or (session['auth_level'] != 2 and session['auth_level'] != 1):
        return redirect(url_for('index'))
    new_asset=add_asset_to_database(request.form)
    return redirect(f"/assets/{new_asset['id']}")

# Create Customer Function - This route is used for a post request to create a new customer. A function is called from the create
# module to create a new customer within the database. Once created, the user is redirected to the single customer page for the 
# new customer.
@app.route('/create/customer', methods=['POST'])
def create_customer():
    if not session.get('logged_in') or (session['auth_level'] != 2 and session['auth_level'] != 1):
        return redirect(url_for('index'))
    new_customer=add_customer_to_database(request.form)
    return redirect(f"/customers/{new_customer['id']}")

# Users Route - This route renders a page to display all the users who are logged on the system. All user routes are only accessable to users with
# level 1 auth. An http post request is used off of a form on the page to call a function from the search module. This filters the users
# retrned on the page.
@app.route('/users', methods=['GET', 'POST'])
def users():
    if not session.get('logged_in') or session['auth_level'] != 1:
       return redirect(url_for('index'))
    if request.method == 'GET':
        search_dict=None
        user_array=return_users(search_dict)
        return render_template("user_management.html",users=user_array)
    if request.method == 'POST':
        search_dict=request.form
        user_array=return_users(search_dict)
        return render_template("user_management.html",users=user_array)

# Single User Route - This route displays a page for a single user. A form is used to opearate a function from the update 
# module to alter a users details via a post request. 
@app.route('/users/<user_id>', methods=['GET', 'POST'])
def single_user(user_id):
    if not session.get('logged_in') or session['auth_level'] != 1:
       return redirect(url_for('index'))
    user_details=return_user_by_id(user_id)
    if request.method == 'GET':
        if not user_details:
            return redirect('/users')
        return render_template("single_user.html", user=user_details,
        customers=supabase.table("customers").select("id", "customer_name").execute().data)
    if request.method == 'POST':
        print(request.form)
        update_user(user_id, request.form)
        return redirect(f'/users/{user_id}')

# Create User Route - This route displays a page to create a new user. An http form is used to send a post request
# that triggers a function from the create module to add the new user to the database. Once created, the user is redirected
# to the single user page for the new user they have created. 
@app.route('/users/create', methods=['GET', 'POST'])
def create_user():
    if not session.get('logged_in') or session['auth_level'] != 1:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template("create_user.html", 
        customers=supabase.table("customers").select("id", "customer_name").execute().data)
    if request.method == 'POST':
        user_details=add_user_to_database(request.form)
        return redirect(f"/users/{user_details['id']}")
        

@app.route('/users/<user_id>/delete', methods=["POST"])
def delete_user(user_id):
    if not session.get('logged_in') and session['auth_level'] != 1:
        return redirect(url_for('index'))
    print(request.form)
    if request.form:
        delete_user_by_id(user_id)
        return (redirect('/users'))
    return (redirect(f'/users/{user_id}'))
    
@app.route('/contact', methods=["GET", "POST"])
def user_requests():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    if request.method == "GET":
        if session["auth_level"] == 1 or session["auth_level"] == 2:
            tickets=return_all_tickets()
            return render_template("contact.html", assets=supabase.table("devices").select("id, hostname").execute().data, 
            customers=supabase.table("customers").select("id", "customer_name").execute().data, statuses=supabase.table("request_statuses").select("id, Value").execute().data,
            devices=supabase.table("devices").select("id, hostname").execute().data ,results=tickets ,request_created=False)
        else:
            return render_template("contact.html", 
            assets=supabase.table("devices").select("id, hostname").eq("customer_id", session["customer_id"]).execute().data, 
            customers=None, request_created=False)
    if request.method == "POST":
        print(request.form)
        create_request(request.form)
        if session["auth_level"] == 1 or session["auth_level"] == 2:
            tickets=return_all_tickets()
            print(tickets)
            return render_template("contact.html", assets=supabase.table("devices").select("id, hostname").execute().data, 
            customers=supabase.table("customers").select("id", "customer_name").execute().data, statuses=supabase.table("request_statuses").select("id, Value").execute().data,
            devices=supabase.table("devices").select("id, hostname").execute().data, results=tickets, request_created=True)
        else:
            return render_template("contact.html", assets=supabase.table("devices").select("id, hostname").eq("customer_id", session["customer_id"]).execute().data,
            customers=None, request_created=True)

@app.route("/user-requests", methods=["POST"])
def search_user_requests():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        return(redirect("/contact"))
    if request.method == "POST":
        print(request.form)
        tickets=search_for_tickets(request.form)
        return render_template("contact.html", assets=supabase.table("devices").select("id, hostname").execute().data, 
                customers=supabase.table("customers").select("id", "customer_name").execute().data, statuses=supabase.table("request_statuses").select("id, Value").execute().data,
                devices=supabase.table("devices").select("id, hostname").execute().data ,results=tickets ,request_created=False)

@app.route("/tickets/<ticket_id>", methods=["GET"])
def display_single_ticket(ticket_id):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        return(redirect("/contact"))
    ticket_details=get_ticket_by_id(ticket_id)
    ticket_details["notes"]=get_ticket_notes(ticket_id)
    if len(ticket_details["notes"]) < 0:
        ticket_details["notes"] = None
    if not ticket_details:
        return redirect("/contact")
    customer_users=return_users({"customer": ticket_details["customers"]["customer_name"]})
    return render_template("single_request.html", ticket=ticket_details, statuses=supabase.table("request_statuses").select("id, Value").execute().data,
                            devices=supabase.table("devices").select("id, hostname").execute().data, 
                            customers=supabase.table("customers").select("id", "customer_name").execute().data,
                            users=customer_users)

@app.route("/tickets/<ticket_id>/addNote",methods=["POST"])
def add_note(ticket_id):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        return(redirect("/contact"))
    if request.method == "POST":
        print(request.form)
        response=add_note_to_ticket(request.form, ticket_id)
        return redirect(f"/tickets/{ticket_id}")

@app.route("/tickets/<ticket_id>/changeDevice", methods=["POST"])
def changeDevice(ticket_id):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        return(redirect("/contact"))
    if request.method == "POST":
        print(request.form)
        response=change_ticket_device(request.form, ticket_id)
        return redirect(f"/tickets/{ticket_id}")


@app.route("/tickets/<ticket_id>/changeCustomer", methods=["POST"])
def changeCustomer(ticket_id):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        return(redirect("/contact"))
    if request.method == "POST":
        response=change_ticket_customer(request.form, ticket_id)
        return redirect(f"/tickets/{ticket_id}")

@app.route("/tickets/<ticket_id>/changeUser", methods=["POST"])
def change_user(ticket_id):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        return(redirect("/contact"))
    if request.method == "POST":
        response=change_ticket_user(request.form, ticket_id)
        return redirect(f"/tickets/{ticket_id}")

@app.route("/tickets/<ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        return(redirect("/contact"))
    if request.method == "POST":
        delete_ticket_by_id(ticket_id)
        return redirect("/contact")

@app.route("/tickets/<ticket_id>/note/<note_id>/delete", methods=["POST"])
def delete_note(ticket_id, note_id):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        return(redirect("/contact"))
    if request.method == "POST":
        delete_note_by_id(note_id)
        return redirect(f"/tickets/{ticket_id}")

@app.route("/tickets/<ticket_id>/reassign", methods=["POST"])
def reassign_ticket(ticket_id):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        return(redirect("/contact"))
    if request.method == "POST":
        ticket_details=get_ticket_by_id(ticket_id)
        if ticket_details["request_statuses"]["Value"] == "New":
            change_ticket_status(ticket_id, 2)
        reassign_ticket_user(ticket_id, session["user_id"])
        return redirect(f"/tickets/{ticket_id}")

@app.route("/tickets/<ticket_id>/close", methods=["POST"])
def close_ticket(ticket_id):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    if session["auth_level"] != 1 and session["auth_level"] != 2:
        return(redirect("/contact"))
    if request.method == "POST":
        closing_user=return_user_by_id(session["user_id"])
        change_ticket_status(ticket_id, 3)
        add_note_to_ticket({"body": f"Ticket closed by {closing_user['username']}", "created_by": session["user_id"]},ticket_id)
        return redirect(f"/tickets/{ticket_id}")

@app.errorhandler(404)
def page_not_found(error):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    return render_template("not_found.html")


@app.errorhandler(500)
def application_error(error):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    return render_template("application_error.html", failed_request=request)

@app.route("/error", methods=["POST"])
def send_error_request():
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    if request.method == "POST":
        response=post_error_form(request.form)
        return redirect("/home")

@app.errorhandler(405)
def invalid_method(error):
    if not session.get("logged_in"):
        return redirect(url_for('index'))
    return render_template("invalid_method.html")
