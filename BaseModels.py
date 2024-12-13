from datetime import date,datetime
from pydantic import BaseModel,EmailStr
from typing import Optional,Union
from decimal import Decimal
from typing import List

class User_Type(BaseModel):
    #user_type_id:int 
    user_type:str

class Users(BaseModel):
    first_name:str
    last_name:str
    business_name:str
    email:EmailStr
    active_status:int 
    password:str
    location:str
    contact:str
    user_type_id:int 
    profile_type_id:int 
class User_SignIn(BaseModel):
    email:EmailStr
    password:str
class Profile_Type(BaseModel):
   # profile_type_id:int 
    profile_type:str

class Profile(BaseModel):
    #profile_id:int 
    Company_Name:str
    Contact_Detail:str
    Experience:str
    Thumbnail_Image:str
    profile_type_id:int 
    user_id:int 

class update_Profile(BaseModel):
    profile_id:int 
    Company_Name:str
    Contact_Detail:str
    Experience:str
    Thumbnail_Image:str
    profile_type_id:int 
    user_id:int 

class Packages(BaseModel):
  #  package_id:int 
    package_name:str
    package_price:int 
    price:int 
    user_id:int

class Package_Details(BaseModel):
  #  package_dtl_id:int 
    package_header_image:str
    # package_image:List[str] 
    package_id:int 

class Package_Details_images(BaseModel):
  #  package_dtl_id:int 
    package_dtl_id:int 
    package_image: str
    image_desc: str 

class Package_images(BaseModel):
    package_id: int
    package_image: str
    image_desc: str 

class Events(BaseModel):
  #  event_id:int 
    event_name:str
    number_of_guests:int  
    package_id:int 
    start_date:date
    end_date:date
    # payment_status:str 
    user_id: int 
    profile_id: int 
    location: str 

class Payments(BaseModel):
 #   payment_id:int 
    payment_amount:int 
    payment_type:str   
    event_id:int 
    package_id:int 
    user_id: int 

class EventCreateRequest(BaseModel):
    event_type: str
    event_name: str
    event_location: str
    event_description: str
    event_date: str
    application_deadline: str
    service_type: List[str]  # list of services like catering, decoration, etc.

class BidRequest(BaseModel):
    user_id: int
    event_id: int
    event_type: str
    bid_amount: int 
    currency: str
    remarks: str = None  # Optional field

class SelectBidRequest(BaseModel):
    event_id: int
    bid_id: int
    event_type: str