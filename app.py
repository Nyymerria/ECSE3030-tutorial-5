import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


@app.get("/devices")
async def get_devices():
    device_list = []
    for device in devices.find():
        device["_id"] = str(device["_id"])
        device_list.append(device)
    return device_list


@app.get("/devices/{name}")
async def get_device(name: str):
    device = devices.find_one({"name": name})
    if device:
        device["_id"] = str(device["_id"])
        return device
    else:
        raise HTTPException(status_code=404, detail="Device not found")


@app.post("/devices", status_code=201)
async def create_device(device: Device):
    if devices.find_one({"name": device.name}):
        raise HTTPException(status_code=409, detail="Device already exists")

    device_dict = device.model_dump()

    result = devices.insert_one(device_dict)

    device_dict["_id"] = str(result.inserted_id)

    return device_dict


@app.put("/devices/{name}")
def update_device(name: str, device: Device):
    device_dict = device.model_dump()

    # URL determines the device name
    device_dict["name"] = name

    existing_device = devices.find_one({"name": name})

    if existing_device:
        devices.replace_one({"name": name}, device_dict)
        return device_dict

    result = devices.insert_one(device_dict)
    device_dict["_id"] = str(result.inserted_id)
    return device_dict

@app.delete("/devices/{name}", status_code=204)
def delete_device(name: str):
    result = devices.delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    return None
