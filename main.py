from db_connection import *
from functions import *
from BaseModels import *
import json

from fastapi import status,FastAPI,HTTPException,Depends,Query
from concurrent.futures import ThreadPoolExecutor

#API instance
app = FastAPI()
 
@app.get("/users_type")
def users_type():  
    error_list = []
    executor = ThreadPoolExecutor()

    def fetch_users_type_data():
        try:
            conn = sqlite3.connect('event_management.db', timeout=10) 
            cursor = conn.cursor()
            # Exclude `user_type_id = 3` from the results
            res = cursor.execute("""SELECT * FROM User_Type WHERE user_type_id != 3""")
            res = cursor.fetchall()
            
            if not res:
                error_list.append("No user types found in the database.")
            
            keys = ['user_type_id', 'user_type']
            user_dict_list = [dict(zip(keys, item)) for item in res]
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        finally:
            conn.commit()
            conn.close()
            return user_dict_list

    future = executor.submit(fetch_users_type_data)
    user_dict_list = future.result()

    # Check if there were any errors
    if error_list:
        return {"errors": error_list}
  
    return {"user_type_detail": user_dict_list}



# Create user type
@app.post("/Create_user_type", status_code=status.HTTP_201_CREATED)
def Create_user_type(user_type: User_Type):
    try:
        # Set a timeout to avoid database locking issues
        conn = sqlite3.connect('event_management.db', timeout=10)  
        cursor = conn.cursor()

        # Insert data into User_Type table
        cursor.execute("""INSERT INTO `User_Type` (user_type) VALUES (?)""",
                       (user_type.user_type,))

        # Commit the transaction
        conn.commit()

        # Fetch all records from User_Type table
        cursor.execute("""SELECT * FROM `User_Type`""")
        res = cursor.fetchall()

        # Prepare the result as a dictionary list
        keys = ['user_type_id', 'user_type']
        user_type_dict_list = [dict(zip(keys, item)) for item in res]
        

    except sqlite3.OperationalError as e:
        # Handle database locking errors or other issues
        return {"error": f"Database operation failed: {e}"}
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()
        return {"user_type": user_type_dict_list}


#update_user_type
@app.post("/update_user_type",status_code=status.HTTP_201_CREATED)
def Update_user_type(update_user_type:User_Type):
    conn = sqlite3.connect('event_management.db', timeout=10) 
    cursor = conn.cursor()
    error_list = []
    try:
        res = cursor.execute(""" Select * from `User_Type` """)
        res =cursor.fetchall();
        user = [user for user in res if user[0]==update_user_type.user_type_id]
        if not user:
           error_list.append("user not found")
          #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UserEmotions ID {update_user_UserEmotions.user_emotion_id} not found")
    except Exception as e:
        error_list.append(f"An error occurred: {str(e)}")
    finally:
        cursor.execute(f"""UPDATE `User_Type` SET `user_type_id`=?,`user_type`= ?  WHERE {update_user_type.user_type_id} = `user_type_id` """,
        (update_user_type.user_type_id,update_user_type.user_type))    
        conn.commit()
    # Check if there were any errors
    if error_list:
        return {"errors": error_list}
   
    res = cursor.execute(""" Select * from `User_Type` """)
    res =cursor.fetchall();
    keys = ['user_type_id','user_type']
    update_user_User_Type = [dict(zip(keys, item)) for item in res]
    conn.commit()
    conn.close()
    return {"update_user_User_Type ":update_user_User_Type}


@app.post("/delete_User_Type", status_code=status.HTTP_201_CREATED)
def delete_user_User_Type(delete_User_Type_id: int):
    conn = sqlite3.connect('event_management.db', timeout=10) 
    cursor = conn.cursor()
    error_list = []

    try:
        # Check if the user_type_id exists in the database
        cursor.execute("SELECT * FROM `User_Type` WHERE user_type_id = ?", (delete_User_Type_id,))
        user = cursor.fetchone()  # Fetch a single row
        
        if not user:
            error_list.append(f"User Type ID {delete_User_Type_id} not found")
        else:
            # If found, delete the user type
            cursor.execute("DELETE FROM `User_Type` WHERE user_type_id = ?", (delete_User_Type_id,))
            conn.commit()
    
    except Exception as e:
        error_list.append(f"An error occurred: {str(e)}")
    
    finally:
        # Return the updated list of User_Type
        cursor.execute("SELECT * FROM `User_Type`")
        res = cursor.fetchall()
        keys = ['user_type_id', 'user_type']
        users_User_Type = [dict(zip(keys, item)) for item in res]
        
        conn.close()
    
    # If there were errors, return them
    if error_list:
        return {"errors": error_list}
    
    return {"users_User_Type": users_User_Type}


#create_SignUp
@app.post("/Create_Users",status_code=status.HTTP_201_CREATED)
def Create_Users(Users:Users):
   
    conn = sqlite3.connect('event_management.db', timeout=10) 
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO `Users` (`first_name`,`last_name`,`business_name`,`email`,`active_status`,`password`,`location`,`contact`,`user_type_id`,`profile_type_id`) VALUES (?,?,?,?,?,?,?,?,?,?) """,
    (Users.first_name,Users.last_name,Users.business_name,Users.email,Users.active_status,hashing_pass(Users.password),Users.location,Users.contact,Users.user_type_id,Users.profile_type_id))    


    conn.commit()
    res = cursor.execute(""" Select * from `Users` """)
    res =cursor.fetchall();
    keys = ['user_id','first_name','last_name','business_name','email','active_status','password','location','contact','user_type_id','profile_type_id']
    users_dict_list = [dict(zip(keys, item)) for item in res]
    conn.commit()
    conn.close()
    return {"users ":users_dict_list}





@app.post("/User_SignIn", status_code=status.HTTP_201_CREATED)
def User_SignIn(Users: User_SignIn):
    error_list = []
    conn = sqlite3.connect('event_management.db', timeout=10)
    cursor = conn.cursor()
    
    try:
        # Retrieve all users from the database
        cursor.execute("SELECT * FROM `Users`")
        db_users = cursor.fetchall()

        for _user in db_users:
            # Check if the email matches
            if _user[4] == Users.email:  # Assuming email is at index 4
                # Check the password
                pass_code = hash_Password_check(Users.password, _user[6])  # Assuming password is at index 6
                if not pass_code:
                    return {"user found": "invalid credentials"}
                
                # Check if the user is active
                if _user[11] != 1:  # Assuming isActive is at index 13
                    return {"error": "User is deactivated"}

                # Fetch the user information with descriptive fields if active
                cursor.execute(f"""
                    SELECT u.user_id, u.first_name, u.last_name, u.business_name, u.email, 
                           u.active_status, u.password, u.location, u.contact, 
                           u.user_type_id, u.profile_type_id, ut.user_type, pt.profile_type
                    FROM Users u
                    LEFT JOIN User_Type ut ON u.user_type_id = ut.user_type_id
                    LEFT JOIN Profile_Type pt ON u.profile_type_id = pt.profile_type_id
                    WHERE u.user_id = {_user[0]} AND u.isActive = 1
                """)
                user_info = cursor.fetchone()

                # Map results to descriptive keys
                user_response = {
                    "user_id": user_info[0],
                    "first_name": user_info[1],
                    "last_name": user_info[2],
                    "business_name": user_info[3],
                    "email": user_info[4],
                    "active_status": user_info[5],
                    "password": user_info[6],
                    "location": user_info[7],
                    "contact": user_info[8],
                    "user_type_id": user_info[9],
                    "profile_type_id": user_info[10],
                    "user_type": user_info[11],
                    "profile_type": user_info[12]
                }
                return {"user found": user_response}

        # If no user was found with matching email
        return {"errors": "invalid credentials"}
    
    except Exception as e:
        error_list.append(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=error_list)
    
    finally: 
        conn.close()
    
# Endpoint to deactivate a user by setting isActive to 0
@app.put("/deactivate_user/{user_id}", status_code=status.HTTP_200_OK)
def deactivate_user(user_id: int):
    conn = sqlite3.connect('event_management.db', timeout=10)
    cursor = conn.cursor()
    
    try:
        # Check if user exists and is currently active
        cursor.execute("SELECT isActive FROM Users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user[0] == 0:
            return {"message": "User is already deactivated"}
        
        # Set isActive to 0 to deactivate the user
        cursor.execute("UPDATE Users SET isActive = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        
        return {"message": f"User with user_id {user_id} has been deactivated"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()

# Endpoint to deactivate a profile by setting isActive to 0
@app.put("/deactivate_profile/{profile_id}", status_code=status.HTTP_200_OK)
def deactivate_profile(profile_id: int):
    conn = sqlite3.connect('event_management.db', timeout=10)
    cursor = conn.cursor()
    
    try:
        # Check if profile exists and is currently active
        cursor.execute("SELECT isActive FROM Profile WHERE profile_id = ?", (profile_id,))
        profile = cursor.fetchone()
        
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile[0] == 0:
            return {"message": "Profile is already deactivated"}
        
        # Set isActive to 0 to deactivate the profile
        cursor.execute("UPDATE Profile SET isActive = 0 WHERE profile_id = ?", (profile_id,))
        conn.commit()
        
        return {"message": f"Profile with profile_id {profile_id} has been deactivated"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()

# Endpoint to activate a user by setting isActive to 0
@app.put("/activate_user/{user_id}", status_code=status.HTTP_200_OK)
def activate_user(user_id: int):
    conn = sqlite3.connect('event_management.db', timeout=10)
    cursor = conn.cursor()
    
    try:
        # Check if user exists and is currently active
        cursor.execute("SELECT isActive FROM Users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user[0] == 1:
            return {"message": "User is already activated"}
        
        # Set isActive to 0 to deactivate the user
        cursor.execute("UPDATE Users SET isActive = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        
        return {"message": f"User with user_id {user_id} has been activated"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()

# Endpoint to activate a profile by setting isActive to 0
@app.put("/activate_profile/{profile_id}", status_code=status.HTTP_200_OK)
def activate_profile(profile_id: int):
    conn = sqlite3.connect('event_management.db', timeout=10)
    cursor = conn.cursor()
    
    try:
        # Check if profile exists and is currently active
        cursor.execute("SELECT isActive FROM Profile WHERE profile_id = ?", (profile_id,))
        profile = cursor.fetchone()
        
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile[0] == 1:
            return {"message": "Profile is already activated"}
        
        # Set isActive to 0 to deactivate the profile
        cursor.execute("UPDATE Profile SET isActive = 1 WHERE profile_id = ?", (profile_id,))
        conn.commit()
        
        return {"message": f"Profile with profile_id {profile_id} has been activated"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()

#create_profile_type
@app.post("/Create_profile_type",status_code=status.HTTP_201_CREATED)
def Create_profile_type(Profile_Type:Profile_Type):
   
    conn = sqlite3.connect('event_management.db', timeout=10) 
    cursor = conn.cursor()
    
        
    cursor.execute("""INSERT INTO `Profile_Type` (profile_type) VALUES (?) """,
    (Profile_Type.profile_type,))   

    conn.commit()
    res = cursor.execute(""" Select * from `Profile_Type` """)
    res =cursor.fetchall();
    keys = ['profile_type_id','profile_type']
    profile_type_dict_list = [dict(zip(keys, item)) for item in res]
    conn.commit()
    conn.close()
    return {"Profile_Type ":profile_type_dict_list}

# Endpoint to delete a profile type by ID
@app.delete("/delete_profile_type/{profile_type_id}", status_code=status.HTTP_200_OK)
def delete_profile_type(profile_type_id: int):
    conn = sqlite3.connect('event_management.db', timeout=10)
    cursor = conn.cursor()
    
    try:
        # Check if the profile type exists
        cursor.execute("SELECT * FROM Profile_Type WHERE profile_type_id = ?", (profile_type_id,))
        profile_type = cursor.fetchone()
        
        if not profile_type:
            raise HTTPException(status_code=404, detail="Profile type not found")
        
        # Delete the profile type
        cursor.execute("DELETE FROM Profile_Type WHERE profile_type_id = ?", (profile_type_id,))
        conn.commit()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    finally:
        conn.close()
    
    return {"message": f"Profile type with ID {profile_type_id} has been deleted successfully."}



@app.get("/profile_type")
def profile_type():  
    error_list = []
    executor = ThreadPoolExecutor()

    def fetch_profile_type_data():
        try:
            conn = sqlite3.connect('event_management.db', timeout=10) 
            cursor = conn.cursor()
            # Exclude `profile_type_id = 7` from the results
            res = cursor.execute("""SELECT * FROM Profile_Type WHERE profile_type_id != 7""")
            res = cursor.fetchall()
            
            if not res:
                error_list.append("No profile types found in the database.")
            
            keys = ['profile_type_id', 'profile_type']
            profile_dict_list = [dict(zip(keys, item)) for item in res]
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        finally:
            conn.commit()
            conn.close()
            return profile_dict_list

    future = executor.submit(fetch_profile_type_data)
    profile_dict_list = future.result()

    # Check if there were any errors
    if error_list:
        return {"errors": error_list}
  
    return {"profile_type_detail": profile_dict_list}




@app.post("/Create_profile", status_code=status.HTTP_201_CREATED)
def create_profile(profile: Profile):
    conn = sqlite3.connect('event_management.db', timeout=10) 
    cursor = conn.cursor()

    # Check if profile_type_id exists in Profile_Type
    cursor.execute("SELECT COUNT(*) FROM Profile_Type WHERE profile_type_id = ?", (profile.profile_type_id,))
    profile_type_exists = cursor.fetchone()[0]

    # Check if user_id exists in Users
    cursor.execute("SELECT COUNT(*) FROM Users WHERE user_id = ?", (profile.user_id,))
    user_exists = cursor.fetchone()[0]

    # If either profile_type_id or user_id does not exist, raise an HTTPException
    if not profile_type_exists:
        conn.close()
        raise HTTPException(status_code=400, detail="Profile Type ID does not exist.")

    if not user_exists:
        conn.close()
        raise HTTPException(status_code=400, detail="User ID does not exist.")

    # Check if the user already has a profile
    cursor.execute("SELECT COUNT(*) FROM Profile WHERE user_id = ?", (profile.user_id,))
    profile_exists = cursor.fetchone()[0]

    if profile_exists:
        conn.close()
        raise HTTPException(status_code=400, detail="A profile already exists for this user.")

    # Insert new profile into the Profile table
    cursor.execute("""
        INSERT INTO Profile (company_name, contact_detail, experience, thumbnail_image, profile_type_id, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (profile.Company_Name, profile.Contact_Detail, profile.Experience, profile.Thumbnail_Image, profile.profile_type_id, profile.user_id))

    conn.commit()

    # Fetch the newly created profile
    cursor.execute("SELECT * FROM Profile WHERE user_id = ?", (profile.user_id,))
    new_profile = cursor.fetchone()
    keys = ['profile_id', 'company_name', 'contact_detail', 'experience', 'thumbnail_image', 'profile_type_id', 'user_id']
    profile_dict = dict(zip(keys, new_profile))

    conn.close()
    
    return {"profile": profile_dict}

#update_profile
@app.post("/update_profile",status_code=status.HTTP_201_CREATED)
def Update_user_type(update_Profile:update_Profile):
    conn = sqlite3.connect('event_management.db', timeout=10)  
    cursor = conn.cursor()
    error_list = []
    try:
        res = cursor.execute(""" Select * from `Profile` """)
        res =cursor.fetchall();
        user = [user for user in res if user[0]==update_Profile.profile_id]
        if not user:
           error_list.append("user not found")
          #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UserEmotions ID {update_user_UserEmotions.user_emotion_id} not found")
    except Exception as e:
        error_list.append(f"An error occurred: {str(e)}")
    finally:
        cursor.execute(f"""UPDATE `Profile` SET `profile_id`=?,`company_name`= ?,`contact_detail`=?,`experience`= ?,`thumbnail_image`=?,`profile_type_id`= ?,`user_id`= ?   WHERE {update_Profile.profile_id} = `profile_id` """,
        (update_Profile.profile_id,update_Profile.Company_Name,update_Profile.Contact_Detail,update_Profile.Experience,update_Profile.Thumbnail_Image,update_Profile.profile_type_id,update_Profile.user_id))    
        conn.commit()
    # Check if there were any errors
    if error_list:
        return {"errors": error_list}
   
    res = cursor.execute(""" Select * from `Profile` """)
    res =cursor.fetchall();
    keys = ['profile_id','company_name','contact_detail','experience','thumbnail_image','profile_type_id','user_id']
    update_user_Profile = [dict(zip(keys, item)) for item in res]
    conn.commit()
    conn.close()
    return {"update_user_Profile ":update_user_Profile}


@app.get("/profiles")
async def profiles():
    error_list = []
    executor = ThreadPoolExecutor()

    def fetch_users_type_data():
        profile_dict_list = []  # Initialize the list here
        try:
            conn = sqlite3.connect('event_management.db', timeout=10)  
            cursor = conn.cursor()
            res = cursor.execute("SELECT * FROM Profile")
            res = cursor.fetchall()
            if not res:
                error_list.append("No profiles found in the database.")
                return profile_dict_list  # Return the empty list if no profiles are found
            
            keys = ['profile_id', 'company_name', 'contact_detail', 'experience', 'thumbnail_image', 'profile_type_id', 'user_id','isActive']
            profile_dict_list = [dict(zip(keys, item)) for item in res]
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        finally:
            conn.commit()
            conn.close()
        return profile_dict_list

    future = executor.submit(fetch_users_type_data)
    profile_dict_list = future.result()

    # Check if there were any errors
    if error_list:
        return {"errors": error_list}
  
    return {"profiles": profile_dict_list}




@app.get("/get_profile_by_user_1d")
async def profile_type(user_id: int):
    error_list = []
    executor = ThreadPoolExecutor()

    def fetch_users_type_data(user_id):
        profile_dict_list = []  # Initialize the list here
        try:
            conn = sqlite3.connect('event_management.db', timeout=10)  
            cursor = conn.cursor()
            # Use parameterized query to prevent SQL injection
            res = cursor.execute("SELECT * FROM Profile WHERE user_id = ?", (user_id,))
            res = cursor.fetchall()
            if not res:
                error_list.append(f"No profiles found for user_id {user_id}.")
                return profile_dict_list  # Return the empty list if no profiles are found
            
            keys = ['profile_id', 'company_name', 'contact_detail', 'experience', 'thumbnail_image', 'profile_type_id', 'user_id']
            profile_dict_list = [dict(zip(keys, item)) for item in res]
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        finally:
            conn.close()  # Close connection in finally block
        return profile_dict_list

    # Pass the user_id to the function
    future = executor.submit(fetch_users_type_data, user_id)
    profile_dict_list = future.result()

    # Check if there were any errors
    if error_list:
        return {"errors": error_list}

    # If no profiles were found for the user_id, raise an HTTP exception
    if not profile_dict_list:
        raise HTTPException(status_code=404, detail="No profiles found for the specified user_id.")
  
    return {"profile_detail": profile_dict_list}

@app.get("/Users")
def Users():  
    error_list = []
    executor = ThreadPoolExecutor()
    def fetch_users_data():
        try:
            conn = sqlite3.connect('event_management.db', timeout=10) 
            cursor = conn.cursor()
            res = cursor.execute(""" Select * from `Users` """)
            res =cursor.fetchall();
            if not res:
               error_list.append("No users found in the database.")
            #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
            keys = ['user_id','first_name','last_name','business_name','email','active_status','password','location','contact','user_type_id','profile_type_id','isActive']
            profile_dict_list = [dict(zip(keys, item)) for item in res]
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        finally:
            conn.commit()
            conn.close()
            return profile_dict_list
    future = executor.submit(fetch_users_data)
    users_dict_list = future.result()

    # Check if there were any errors
    if error_list:
        return {"errors": error_list}
  
    return {"users ":users_dict_list}




@app.post("/Create_Package", status_code=status.HTTP_201_CREATED)
def Create_Package(Package: Packages):
    conn = sqlite3.connect('event_management.db', timeout=10) 
    cursor = conn.cursor()

    # Insert the new package
    cursor.execute(
        """INSERT INTO Packages (package_name, package_price, price, user_id) VALUES (?, ?, ?, ?)""",
        (Package.package_name, Package.package_price, Package.price, Package.user_id)
    )
    
    # Get the ID of the newly created package
    package_id = cursor.lastrowid

    # Commit the transaction
    conn.commit()

    # Fetch the newly created package details
    cursor.execute("SELECT * FROM Packages WHERE package_id = ?", (package_id,))
    res = cursor.fetchone()
    
    keys = ['package_id', 'package_name', 'package_price', 'price', 'user_id']
    new_package = dict(zip(keys, res))

    # Close the connection
    conn.close()

    return {"package": new_package}


@app.get("/Packages")
def Packages():  
    error_list = []
    executor = ThreadPoolExecutor()
    def fetch_Packages_data():
        try:
            conn = sqlite3.connect('event_management.db', timeout=10) 
            cursor = conn.cursor()
            res = cursor.execute(""" Select * from `Packages` """)
            res =cursor.fetchall();
            if not res:
               error_list.append("No users found in the database.")
            #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
            keys = ['package_id','package_name','package_price','price','user_id']
            profile_dict_list = [dict(zip(keys, item)) for item in res]
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        finally:
            conn.commit()
            conn.close()
            return profile_dict_list
    future = executor.submit(fetch_Packages_data)
    Packages_dict_list = future.result()
    if error_list:
        return {"errors": error_list}
  
    return {"Packages ":Packages_dict_list}


#Create Package_Details
@app.post("/Create_Package_Details",status_code=status.HTTP_201_CREATED)
def Create_Package_Details(Package_Details:Package_Details):
   
    conn = sqlite3.connect('event_management.db', timeout=10) 
    cursor = conn.cursor()
    
    cursor.execute("""INSERT INTO `Package_Details` (`package_header_image`,`package_id`) VALUES (?,?) """,
    (Package_Details.package_header_image,Package_Details.package_id))    

    conn.commit()
    # Retrieve the last inserted package details record
    new_package_dtl_id = cursor.lastrowid
    cursor.execute("SELECT * FROM Package_Details WHERE package_dtl_id = ?", (new_package_dtl_id,))
    result = cursor.fetchone()
    keys = ['package_dtl_id','package_header_image','package_id']
    package_details_data = dict(zip(keys, result))
    conn.close()
    return {"Package_Details ":package_details_data}


@app.get("/Package_Details", status_code=status.HTTP_200_OK)
def get_package_details(user_id: int = Query(..., description="ID of the user to fetch packages for")):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('event_management.db', timeout=10)
        cursor = conn.cursor()

        # Fetch all packages created by the user
        cursor.execute("SELECT * FROM Packages WHERE user_id = ?", (user_id,))
        packages_results = cursor.fetchall()
        all_packages = {}
        for package in packages_results:
            package_id, package_name, package_price, price, user_id_db = package
            if package_id not in all_packages:
                all_packages[package_id] = {
                    "package_id": package_id,
                    "package_name": package_name,
                    "package_price": package_price,
                    "price": price,
                    "package_details": [],
                    "package_images": []
                }
            cursor.execute("SELECT * FROM Package_Details WHERE package_id = ?", (package_id,))
            package_details_results = cursor.fetchall()

            # Process Package_Details results
            for detail in package_details_results:
                package_dtl_id, package_header_image, _ = detail
                all_packages[package_id]["package_details"].append({
                    "package_dtl_id": package_dtl_id,
                    "package_header_image": package_header_image
                })

            # Fetch images from Package_images table for the current package_id
            cursor.execute("SELECT * FROM Package_images WHERE package_id = ?", (package_id,))
            package_images_results = cursor.fetchall()

            # Process Package_images results
            for image in package_images_results:
                package_image_id, _, package_image, image_desc = image
                all_packages[package_id]["package_images"].append({
                    "package_image_id": package_image_id,
                    "package_image": package_image,
                    "image_desc": image_desc,
                })

        # If no packages were found for the user, return a message
        if not all_packages:
            return {"message": f"No packages found for user_id {user_id}."}

    except Exception as e:
        # Handle any exception that occurs
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        # Close the database connection
        conn.close()

    # Return the package data for the specified user_id, including the user_id in the response
    return {
        "user_id": user_id,
        "all_packages": list(all_packages.values())
    }


# Endpoint to create a new Package_Details_images entry
@app.post("/Package_images", status_code=status.HTTP_201_CREATED)
def Package_images(image_data: Package_images):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('event_management.db', timeout=10)
        cursor = conn.cursor()

        # Insert new data into Package_Details_images table
        cursor.execute('''
            INSERT INTO Package_images (package_id, package_image, image_desc)
            VALUES (?, ?, ?)
        ''', (image_data.package_id, image_data.package_image, image_data.image_desc))

        # Commit the transaction
        conn.commit()

        # Retrieve the newly created row to confirm it was successfully inserted
        new_id = cursor.lastrowid  # Get the ID of the last inserted row
        cursor.execute('SELECT * FROM Package_images WHERE Package_image_id = ?', (new_id,))
        result = cursor.fetchone()

        # Define keys to map to the columns in the table
        keys = ['Package_image_id', 'package_id', 'package_image', 'image_desc']
        package_image = dict(zip(keys, result))

    except Exception as e:
        # Handle any exception that occurs
        conn.rollback()  # Rollback the transaction if there was an error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        # Close the database connection
        conn.close()

    # Return the newly created Package_Details_images data
    return {"package_image": package_image}


@app.get("/get_Package_images", status_code=status.HTTP_200_OK)
def get_Package_images():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('event_management.db', timeout=10)
        cursor = conn.cursor()

        # Fetch all rows from the Package_Details_images table
        cursor.execute('SELECT * FROM Package_images')
        results = cursor.fetchall()

        # Define keys to map to the columns in the table
        keys = ['Package_image_id', 'package_id', 'package_image', 'image_desc']
        package_images_list = [dict(zip(keys, result)) for result in results]

    except Exception as e:
        # Handle any exception that occurs
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        # Close the database connection
        conn.close()

    # Return all Package_Details_images data
    return {"Package_images": package_images_list}



@app.post("/Create_Book_Event", status_code=status.HTTP_201_CREATED)
def Create_Book_Event(event: Events):
    conn = sqlite3.connect('event_management.db', timeout=10)
    cursor = conn.cursor()

    # Insert the new event
    cursor.execute(
        """
        INSERT INTO Events (event_name, number_of_guests, package_id, start_date, end_date,user_id,profile_id,location)
        VALUES (?, ?, ?, ?, ?, ?,?,?)
        """,
        (event.event_name, event.number_of_guests, event.package_id, event.start_date.strftime("%Y-%m-%d"),event.end_date.strftime("%Y-%m-%d"), event.user_id,event.profile_id,event.location)
    )

    event_id = cursor.lastrowid

    # Fetch only the newly created event
    cursor.execute("SELECT * FROM Events WHERE event_id = ?", (event_id,))
    row = cursor.fetchone()

    keys = ['event_id', 'event_name', 'number_of_guests', 'package_id', 'start_date', 'end_date', 'user_id','profile_id','location','payment_status']
    created_event = dict(zip(keys, row))

    conn.commit()
    conn.close()

    return {"Event": created_event}


#Get Book Event
@app.get("/Book_Event")
def Book_Event():  
    error_list = []
    executor = ThreadPoolExecutor()
    def fetch_Book_Event_data():
        try:
            conn = sqlite3.connect('event_management.db', timeout=10) 
            cursor = conn.cursor()
            res = cursor.execute(""" Select * from `Events` """)
            res =cursor.fetchall();
            if not res:
               error_list.append("No users found in the database.")
            #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
            keys = ['event_id','event_name','number_of_guests','package_id','start_date','end_date','user_id','profile_id','location','payment_status']
            profile_dict_list = [dict(zip(keys, item)) for item in res]
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        finally:
            conn.commit()
            conn.close()
            return profile_dict_list
    future = executor.submit(fetch_Book_Event_data)
    Book_Event_dict_list = future.result()

    # Check if there were any errors
    if error_list:
        return {"errors": error_list}
  
    return {"Book_Events ":Book_Event_dict_list}


@app.get("/Booked_Events/{user_id}")
async def Booked_Events(user_id: int):
    # Establish a database connection
    conn = sqlite3.connect('event_management.db', timeout=10)
    cursor = conn.cursor()

    # Step 1: Check if the user exists and retrieve their details
    user_query = '''
    SELECT first_name, last_name, business_name, email, location, contact
    FROM Users
    WHERE user_id = ?
    '''
    cursor.execute(user_query, (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    user_data = {
        "user_details": {
            "first_name": user[0],  # index 0 corresponds to first_name
            "last_name": user[1],   # index 1 corresponds to last_name
            "business_name": user[2],
            "email": user[3],
            "location": user[4],
            "contact": user[5]
        },
        "profiles": []
    }

    # Step 2: Retrieve profiles for the given user_id
    profile_query = '''
    SELECT profile_id, company_name, contact_detail, experience, thumbnail_image
    FROM Profile
    WHERE user_id = ?
    '''
    cursor.execute(profile_query, (user_id,))
    profiles = cursor.fetchall()

    if profiles:
        # Step 3: For each profile, retrieve events associated with the profile_id
        for profile in profiles:
            profile_data = {
                "profile_id": profile[0],         # index 0 corresponds to profile_id
                "company_name": profile[1],       # index 1 corresponds to company_name
                "contact_detail": profile[2],     # index 2 corresponds to contact_detail
                "experience": profile[3],         # index 3 corresponds to experience
                "thumbnail_image": profile[4],    # index 4 corresponds to thumbnail_image
                "events": []
            }

            events_query = '''
            SELECT event_id, event_name, number_of_guests, start_date, end_date, location, payment_status, user_id
            FROM Events
            WHERE profile_id = ?
            '''
            cursor.execute(events_query, (profile[0],))  # profile[0] is the profile_id
            events = cursor.fetchall()

            # For each event, fetch user details from the Users table
            for event in events:
                event_data = {
                    "event_id": event[0],             # index 0 corresponds to event_id
                    "event_name": event[1],           # index 1 corresponds to event_name
                    "number_of_guests": event[2],     # index 2 corresponds to number_of_guests
                    "start_date": event[3],           # index 3 corresponds to start_date
                    "end_date": event[4],             # index 4 corresponds to end_date
                    "location": event[5],             # index 5 corresponds to location
                    "payment_status": event[6]        # index 6 corresponds to payment_status
                }
                user_id_from_event = event[7]  # index 7 corresponds to user_id from the event
                user_query_for_event = '''
                SELECT first_name, last_name, business_name, email, location, contact
                FROM Users
                WHERE user_id = ?
                '''
                cursor.execute(user_query_for_event, (user_id_from_event,))
                user_from_event = cursor.fetchone()

                if user_from_event:
                    event_data["user_info_who_booked_event"] = {
                        "first_name": user_from_event[0],  # index 0 corresponds to first_name
                        "last_name": user_from_event[1],   # index 1 corresponds to last_name
                        "business_name": user_from_event[2],
                        "email": user_from_event[3],
                        "location": user_from_event[4],
                        "contact": user_from_event[5]
                    }

                profile_data["events"].append(event_data)

            user_data["profiles"].append(profile_data)

    # Step 4: Return the collected data
    conn.close()
    return user_data





@app.get("/checklist_of_events", status_code=status.HTTP_200_OK)
def checklist_of_events(user_id: int = Query(..., description="ID of the user to fetch events for")):
    error_list = []
    executor = ThreadPoolExecutor()

    def fetch_events_for_user():
        events_list = []
        try:
            conn = sqlite3.connect('event_management.db', timeout=10)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT e.event_id, e.event_name, e.number_of_guests, e.package_id, e.start_date, e.end_date,
                       e.user_id, e.payment_status, e.profile_id, p.company_name, pt.profile_type
                FROM Events e
                JOIN Profile p ON e.profile_id = p.profile_id
                JOIN Profile_Type pt ON p.profile_type_id = pt.profile_type_id
                WHERE e.user_id = ? AND e.payment_status = 'Pending'
            """, (user_id,))
            results = cursor.fetchall()
            
            if not results:
                error_list.append(f"No pending events found for user_id {user_id}.")
                return events_list
            
            # Map database fields to dictionary keys
            keys = ['event_id', 'event_name', 'number_of_guests', 'package_id', 'start_date', 'end_date',
                    'user_id', 'payment_status', 'profile_id', 'company_name', 'profile_type']
            events_list = [dict(zip(keys, event)) for event in results]
        
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        
        finally:
            conn.close()
        
        return events_list

    # Execute the fetch operation in a separate thread
    future = executor.submit(fetch_events_for_user)
    events_list = future.result()

    # If errors were collected, return them in the response
    if error_list:
        return {"errors": error_list}

    return {"events": events_list}


@app.post("/Create_Payments", status_code=status.HTTP_201_CREATED)
def create_payment(payment: Payments):
    conn = sqlite3.connect('event_management.db', timeout=10)
    cursor = conn.cursor()

    # Insert new payment
    cursor.execute("""
        INSERT INTO Payments (payment_amount, payment_type, event_id, package_id, user_id)
        VALUES (?, ?, ?, ?, ?)
    """, (payment.payment_amount, payment.payment_type, payment.event_id, payment.package_id, payment.user_id))

    # Commit the transaction
    conn.commit()

    # Retrieve the last inserted payment record
    new_payment_id = cursor.lastrowid
    cursor.execute("SELECT * FROM Payments WHERE payment_id = ?", (new_payment_id,))
    result = cursor.fetchone()
    keys = ['payment_id', 'payment_amount', 'payment_type', 'payment_status', 'event_id', 'package_id', 'user_id']
    payment_data = dict(zip(keys, result))

    cursor.execute("""
        UPDATE Events
        SET payment_status = 'Payment Transferred'
        WHERE event_id = ?
    """, (payment.event_id,))
    
    conn.commit()
    conn.close()

    return {"Payment": payment_data}




#Get Payments
@app.get("/Payments")
def Payments():  
    error_list = []
    executor = ThreadPoolExecutor()
    def fetch_Payments_data():
        try:
            conn = sqlite3.connect('event_management.db', timeout=10) 
            cursor = conn.cursor()
            res = cursor.execute(""" Select * from `Payments` """)
            res =cursor.fetchall();
            if not res:
               error_list.append("No users found in the database.")
            #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
            keys = keys = ['payment_id','payment_amount','payment_type','payment_status','event_id','package_id','user_id']
            profile_dict_list = [dict(zip(keys, item)) for item in res]
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        finally:
            conn.commit()
            conn.close()
            return profile_dict_list
    future = executor.submit(fetch_Payments_data)
    Payments_dict_list = future.result()

    # Check if there were any errors
    if error_list:
        return {"errors": error_list}
  
    return {"Payments ":Payments_dict_list}

# Function to create a new event
@app.post("/create_event/")
def create_event(event: EventCreateRequest, user_id: int):

    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()

    cursor.execute('SELECT profile_type_id FROM Users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    # Check if user is an event organizer (profile_type_id == 5)
    if not result or result[0] != 5:
        conn.close()
        raise HTTPException(status_code=403, detail="Permission denied: User is not an event organizer")
    # Convert service_type list to a comma-separated string to store in the database
    service_type_str = ','.join(event.service_type)

    # Insert the new event into the Event_Organisers table
    cursor.execute('''
        INSERT INTO Event_Organisers (
            event_type, event_name, event_location, event_description, event_date, 
            application_deadline, service_type, profile_type_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (event.event_type, event.event_name, event.event_location, event.event_description, 
          event.event_date, event.application_deadline, service_type_str, user_id))

    # Commit the transaction and retrieve the new event's ID
    conn.commit()
    new_event_id = cursor.lastrowid
    conn.close()

    # Return a success message with the generated event ID
    return {"message": "Event created successfully", "event_id": new_event_id}

# Get Event List
@app.get("/get_event_by_Event_Organisers")
def Get_event_by_Event_Organisers():  
    error_list = []
    executor = ThreadPoolExecutor()
    def fetch_Event_Organisers_data():
        try:
            conn = sqlite3.connect('event_management.db', timeout=10) 
            cursor = conn.cursor()
            res = cursor.execute(""" Select * from `Event_Organisers` """)
            res =cursor.fetchall();
            if not res:
               error_list.append("No event found in the database.")
            #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
            keys = ['event_id','event_type','event_name','event_location','event_description','event_date','application_deadline','service_type','profile_type_id']
            profile_dict_list = [dict(zip(keys, item)) for item in res]
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        finally:
            conn.commit()
            conn.close()
            return profile_dict_list
    future = executor.submit(fetch_Event_Organisers_data)
    events_dict_list = future.result()

    # Check if there were any errors
    if error_list:
        return {"errors": error_list}
  
    return {"Events ":events_dict_list}

# Endpoint to submit a new bid
@app.post("/submit_bid/")
async def submit_bid(bid: BidRequest):
    # Check if the user exists
    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE user_id = ?', (bid.user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the event exists
    cursor.execute('SELECT * FROM Event_Organisers WHERE organiser_event_id = ?', (bid.event_id,))
    event = cursor.fetchone()
    
    if not event:
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")

    # Insert the bid into the Mark_bidding table
    cursor.execute('''
        INSERT INTO Mark_bidding (user_id, event_id, event_type, bid_amount, currency, remarks)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (bid.user_id, bid.event_id, bid.event_type, bid.bid_amount, bid.currency, bid.remarks))

    conn.commit()
    conn.close()

    return {"message": "Bid submitted successfully!"}

# view bidding
@app.get("/view_bidding")
def View_bidding():  
    error_list = []
    executor = ThreadPoolExecutor()
    def fetch_bidding__data():
        try:
            conn = sqlite3.connect('event_management.db', timeout=10) 
            cursor = conn.cursor()
            res = cursor.execute(""" Select * from `Mark_bidding` """)
            res =cursor.fetchall();
            if not res:
               error_list.append("No event found in the database.")
            #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
            keys = ['bid_id','user_id','event_id','event_type','bid_amount','currency','remarks','status']
            bid_dict_list = [dict(zip(keys, item)) for item in res]
        except Exception as e:
            error_list.append(f"An error occurred: {str(e)}")
        #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        finally:
            conn.commit()
            conn.close()
            return bid_dict_list
    future = executor.submit(fetch_bidding__data)
    bidding_dict_list = future.result()

    # Check if there were any errors
    if error_list:
        return {"errors": error_list}
  
    return {"Biddings_data ":bidding_dict_list}

# Endpoint to select the winning bid
@app.post("/select_bid/")
async def select_bid(select_bid: SelectBidRequest):

    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()
    # Check if the event exists
    cursor.execute('SELECT * FROM Event_Organisers WHERE organiser_event_id = ? AND event_type = ?', 
                   (select_bid.event_id, select_bid.event_type))
    event = cursor.fetchone()
    
    if not event:
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if the bid exists for the event in Mark_bidding
    cursor.execute('SELECT * FROM Mark_bidding WHERE bid_id = ? AND event_id = ?', 
                   (select_bid.bid_id, select_bid.event_id))
    bid = cursor.fetchone()

    if not bid:
        conn.close()
        raise HTTPException(status_code=404, detail="Bid not found for this event")

    # Update the Mark_bidding table to set status to "closed"
    cursor.execute('''
        UPDATE Mark_bidding
        SET status = 'closed'
        WHERE bid_id = ?
    ''', (select_bid.bid_id,))
    
    conn.commit()
    selected_bid = {
        "bid_id": bid[0],  # Assuming bid_id is the first column in Mark_bidding
        "event_id": bid[1],  # Assuming event_id is the second column in Mark_bidding
        "event_type": bid[2],  # Assuming event_type is the third column in Mark_bidding
        "bid_amount": bid[3]  # Assuming bid_amount is the fourth column in Mark_bidding
    }

    conn.close()

    return {"selected_bid": selected_bid}





def get_user_by_id(user_id: int):
    conn = sqlite3.connect('event_management.db', timeout=10)
    cursor = conn.cursor()

    # Fetch main user details
    cursor.execute('''
        SELECT u.user_id, u.first_name, u.last_name, u.business_name, u.email, 
               u.active_status, u.location, u.contact,
               ut.user_type, pt.profile_type
        FROM Users u
        LEFT JOIN User_Type ut ON u.user_type_id = ut.user_type_id
        LEFT JOIN Profile_Type pt ON u.profile_type_id = pt.profile_type_id
        WHERE u.user_id = ?
    ''', (user_id,))
    user_row = cursor.fetchone()
    
    if not user_row:
        conn.close()
        return None  # User not found

    # Define basic user info keys
    user_keys = ["user_id", "first_name", "last_name", "business_name", "email",
                 "active_status", "location", "contact", "user_type", "profile_type"]
    user_info = dict(zip(user_keys, user_row))

    # Fetch packages for this user
    cursor.execute('''
        SELECT package_name, package_price FROM Packages WHERE user_id = ?
    ''', (user_id,))
    packages = [{"package_name": row[0], "package_price": row[1]} for row in cursor.fetchall()]
    user_info["packages"] = packages

    # Fetch events for this user
    cursor.execute('''
        SELECT event_name, number_of_guests, start_date, end_date FROM Events WHERE user_id = ?
    ''', (user_id,))
    events = [{"event_name": row[0], "number_of_guests": row[1], "start_date": row[2], "end_date": row[3]} for row in cursor.fetchall()]
    user_info["events"] = events

    # Fetch payments for this user
    cursor.execute('''
        SELECT payment_amount, payment_type, payment_status FROM Payments WHERE user_id = ?
    ''', (user_id,))
    payments = [{"payment_amount": row[0], "payment_type": row[1], "payment_status": row[2]} for row in cursor.fetchall()]
    user_info["payments"] = payments

    # Fetch bidding details for this user
    cursor.execute('''
        SELECT event_type, bid_amount, currency, remarks FROM Mark_bidding WHERE user_id = ?
    ''', (user_id,))
    bids = [{"event_type": row[0], "bid_amount": row[1], "currency": row[2], "remarks": row[3]} for row in cursor.fetchall()]
    user_info["bids"] = bids

    conn.close()
    return user_info

# Endpoint to get user profile with all related information
@app.get("/user_profiles_information", status_code=status.HTTP_200_OK)
def get_user_profile(user_id: int):
    user_info = get_user_by_id(user_id)
    if not user_info:
        return {"message": "User not found"}
    return {"user": user_info}



@app.get("/packages_info/")
def get_user_packages(user_id: int):
    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Packages.package_id, Packages.package_name
        FROM Users
        JOIN Packages ON Users.user_id = Packages.user_id
        WHERE Users.user_id = ?
    ''', (user_id,))

    packages_info = [{"package_id": row[0], "package_name": row[1]} for row in cursor.fetchall()]

    conn.close()
    return {"packages_info": packages_info}

@app.get("/all_profiles_info/")
def get_profiles(profile_number: int = Query(..., description="Profile number (1 for event organizer, 2 for venue provider, 3 for other profiles)")):
    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()
    
    # Define profile type mappings
    profile_type_map = {
        1: "event organizer",
        2: "Venue Provider"
    }

    # If profile_number is 1 or 2, get specific profile types that are active
    if profile_number in profile_type_map:
        profile_type = profile_type_map[profile_number]
        cursor.execute('''
            SELECT Profile.profile_id, Profile.company_name, Profile.contact_detail, Profile.experience, 
                   Profile.thumbnail_image, Profile_Type.profile_type, Profile.user_id
            FROM Profile
            INNER JOIN Profile_Type ON Profile.profile_type_id = Profile_Type.profile_type_id
            WHERE Profile_Type.profile_type = ? AND Profile.isActive = 1
        ''', (profile_type,))
    
    # If profile_number is 3, get all active profiles except "event organizer", "Venue Provider", "Super Admin", and "Admin"
    elif profile_number == 3:
        cursor.execute('''
            SELECT Profile.profile_id, Profile.company_name, Profile.contact_detail, Profile.experience, 
                   Profile.thumbnail_image, Profile_Type.profile_type, Profile.user_id
            FROM Profile
            INNER JOIN Profile_Type ON Profile.profile_type_id = Profile_Type.profile_type_id
            WHERE Profile_Type.profile_type NOT IN ('event organizer', 'Venue Provider', 'Super Admin', 'Admin')
            AND Profile.isActive = 1
        ''')
    
    # Invalid profile_number
    else:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid profile number. Use 1 for event organizer, 2 for venue provider, 3 for other profiles.")
    
    profiles = [
        {
            "profile_id": row[0],
            "company_name": row[1],
            "contact_detail": row[2],
            "experience": row[3],
            "thumbnail_image": row[4],
            "profile_type": row[5],
            "user_id": row[6]  # Include user_id in the response
        }
        for row in cursor.fetchall()
    ]

    conn.close()

    return {"profiles": profiles}



if __name__ == "__main__":
    #Testing
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10029)
    conn.close()
