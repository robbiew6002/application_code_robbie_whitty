import os
from supabase import create_client, Client
url: str = "https://xhntkwdrchzgorlowvgf.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhobnRrd2RyY2h6Z29ybG93dmdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk0NjM4MjUsImV4cCI6MjA2NTAzOTgyNX0.U90qN6hXu4Leqs4-KhnThdvhNLQzczcWjckN3Bn_Zec"
supabase: Client = create_client(url, key)
