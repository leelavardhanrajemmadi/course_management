import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables from the .env file
load_dotenv()

app = FastAPI(
    title="Warehouse Inventory API",
    description="Production-grade API for tracking transit and inventory between warehouses.",
    version="1.0.0"
)

# --- Database Connection ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Critical: Supabase environment variables are missing.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Pydantic Schemas (The Bouncers) ---
class DispatchRequest(BaseModel):
    product_name: str = Field(..., min_length=2, description="Name of the product")
    quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")

class ShipmentResponse(BaseModel):
    id: int
    product_name: str
    quantity: int
    status: str
    
class InventoryItem(BaseModel):
    product_name: str
    quantity: int

# ---------------------------------------------------------
# Feature 1: Dispatch Stock (Warehouse A -> B)
# ---------------------------------------------------------
@app.post("/dispatch_stock", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
def dispatch_stock(data: DispatchRequest):
    new_shipment = {
        "product_name": data.product_name,
        "quantity": data.quantity,
        "status": "In Transit"
    }
    
    response = supabase.table("transit_log").insert(new_shipment).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to log shipment in the database.")
        
    return response.data[0]

# ---------------------------------------------------------
# Feature 2: View Transit Log
# ---------------------------------------------------------
@app.get("/shipments", response_model=List[ShipmentResponse])
def get_shipments(status_filter: Optional[str] = None):
    # Added an optional query parameter to filter by status (e.g., ?status_filter=In Transit)
    query = supabase.table("transit_log").select("*")
    
    if status_filter:
        query = query.eq("status", status_filter)
        
    response = query.execute()
    return response.data

# ---------------------------------------------------------
# Feature 3: Receive Stock (The Core Transaction)
# ---------------------------------------------------------
@app.put("/receive_stock/{shipment_id}")
def receive_stock(shipment_id: int):
    # 1. Validate Shipment Exists
    shipment_response = supabase.table("transit_log").select("*").eq("id", shipment_id).execute()
    
    if not shipment_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Shipment {shipment_id} not found.")
        
    shipment = shipment_response.data[0]
    
    # 2. Prevent Double-Receiving
    if shipment["status"] == "Received":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Shipment has already been processed.")
    
    product_name = shipment["product_name"]
    quantity_received = shipment["quantity"]
    
    # 3. Update Shipment Status
    update_res = supabase.table("transit_log").update({"status": "Received"}).eq("id", shipment_id).execute()
    if not update_res.data:
        raise HTTPException(status_code=500, detail="Failed to update shipment status.")
    
    # 4. Inventory Upsert Logic
    inventory_response = supabase.table("master_inventory").select("quantity").eq("product_name", product_name).execute()
    
    if inventory_response.data:
        new_quantity = inventory_response.data[0]["quantity"] + quantity_received
        supabase.table("master_inventory").update({"quantity": new_quantity}).eq("product_name", product_name).execute()
    else:
        supabase.table("master_inventory").insert({"product_name": product_name, "quantity": quantity_received}).execute()
        
    return {"status": "success", "message": f"Shipment {shipment_id} received. {quantity_received} units of {product_name} added to inventory."}

# ---------------------------------------------------------
# Feature 4: View Master Inventory
# ---------------------------------------------------------
@app.get("/inventory", response_model=List[InventoryItem])
def get_inventory():
    response = supabase.table("master_inventory").select("*").execute()
    return response.data