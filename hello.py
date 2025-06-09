from flask import Flask
from supabaseClient import supabase
app = Flask(__name__)

response = (
    supabase.table("users")
    .select("*")
    .execute()
)


@app.route("/")
def hello_world():
    return "Hello, World!"