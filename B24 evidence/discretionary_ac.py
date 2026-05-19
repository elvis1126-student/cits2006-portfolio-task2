# discretionary access control

import json
import time
Master_key = 'elvis'
# user class to hold user information
class User:
    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name

# resource class to hold resource information
class Resource:
    def __init__(self,owner_id,owner_name,resource_name):
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.resource_name = resource_name
        self.permission = {}

    def grant_permission(resource, owner, granted_user, permission):
        #check if the person is the owner
        if owner.user_id != resource.owner_id:
            print("[!] Only the owner can change permissions.")
            return None
        
        if permission not in ["read", "write","execute"]:
            print(f"[!] Invalid permission '{permission}'")
            print(f"[i] We current only support read, write and execute")
            return

        #new person, new permissions list
        if granted_user.user_id not in resource.permission:
            resource.permission[granted_user.user_id] = []
            resource.permission[granted_user.user_id].append(permission)
            print(f"[+] {owner.user_name} granted '{permission}' to {granted_user.user_name} on '{resource.resource_name}'")
        # old person, new permission
        elif permission not in resource.permission[granted_user.user_id]:
            resource.permission[granted_user.user_id].append(permission)
            print(f"[+] {owner.user_name} granted new '{permission}' to {granted_user.user_name} on '{resource.resource_name}'")
        # permission already granted
        else:
            print(f"[i] {granted_user.user_name} has '{permission}' on '{resource.resource_name}'")
        
        #print("Saving:", resource.resource_name, resource.permission)
        #write out to json
        write_out_resource_permission(resource)
        

    def remove_permission(resource, owner, removed_user, permission):
        #check if the person is the owner
        if owner.user_id != resource.owner_id:
            print("[!] Only owner can change permissions")
            return None
    
        #removing privilege from user
        if removed_user.user_id in resource.permission and permission in resource.permission[removed_user.user_id]:
            print(resource.permission)
            resource.permission[removed_user.user_id].remove(permission) 
            print(resource.permission)

            if resource.permission[removed_user.user_id] == []:
                del resource.permission[removed_user.user_id] #?

            print(f"[-] Removed '{permission}' from {removed_user.user_name} on '{resource.resource_name}'.")
        
        elif removed_user.user_id not in resource.permission:
             print(f"[i] The owner: {owner.user_id} never being granted with any privilege to user: {removed_user.user_name}") 
        
        elif permission not in resource.permission[removed_user.user_id]:
            print(f"[i] privilege never granted to user: {removed_user.user_name}")
        #write out to json
        write_out_resource_permission(resource)

    def permission_check(resource, user):
        if user.user_id == resource.owner_id:
            print(f"[^_^] {user.user_name} is the owner of '{resource.resource_name}'")
            return True
        elif user.user_id in resource.permission:
            print(f"[^_^] {user.user_id} have {resource.permission[user.user_id]} privilege")
            return True
        else:
            print(f"[?!] {user.user_name} has no privileges on '{resource.resource_name}'.")
            return False



def load_data_from_json(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return [] 

def save_data_to_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def load_back_resource_permission(resource_name):
    for item in load_data_from_json("resource_permission.json"):
        if resource_name == item["resource_name"]:
            resource = Resource(item["owner_id"],item["owner_name"],item["resource_name"])
            resource.permission = item["permission"]
            return resource
    return None

def load_back_user_information(user_id):
    for user in load_data_from_json("user.json"):
        if user_id == user["user_id"]:
            users = User(user["user_id"],user["user_name"])
            return users
    return None

def write_out_resource_permission(resource):
    #open the original json file and get resource information
    data_permission_list = load_data_from_json("resource_permission.json")

    #new resource
    data_permission_single = {
        "owner_id": resource.owner_id,
        "owner_name": resource.owner_name,
        "resource_name": resource.resource_name,
        "permission": resource.permission
    }

    #check for existance and update
    found = False
    for item in data_permission_list:
        if item["resource_name"] == resource.resource_name:
            item["permission"] = resource.permission
            found = True
            break
    #add to the list that store new resource information
    if not found:
        data_permission_list.append(data_permission_single)

    #write out and update
    save_data_to_json("resource_permission.json",data_permission_list)

def write_out_user_information(user):
    user_information_list = load_data_from_json("user.json")
    user_information = {
        "user_id": user.user_id,
        "user_name": user.user_name
    }

    #check for duplicate
    found = False
    for item in user_information_list:
        if item["user_id"] == user.user_id:
            found = True
            print(f"[i] user id '{user.user_id}' already register")
            break

    #add to the list that store new resource information
    if not found:
        user_information_list.append(user_information)

    save_data_to_json("user.json",user_information_list)
    print(f"[+] User '{user.user_name}' (ID: {user.user_id}) registered.")
    
def delete_user_from_file(user_id):
    user_information_list = load_data_from_json("user.json")
    updated_list = []
    for i in user_information_list:
        if i["user_id"] != user_id:
            updated_list.append(i)
    
    if len(updated_list) == len(user_information_list):
        return False
    
    save_data_to_json("user.json",updated_list)
    return True

def delete_resource_from_file(resource_name):
    data_permission_list = load_data_from_json("resource_permission.json")
    updated_list = []
    for i in data_permission_list:
        if i["resource_name"] != resource_name:
            updated_list.append(i)
    
    if len(updated_list) == len(data_permission_list):
        # some error
        return False
    
    save_data_to_json("resource_permission.json",updated_list)
    return True

# ------------------------
# action

def add_new_user():
    #create user
    print("\nTo Add Please Enter:")
    username = input("username:").strip()
    user_id = input("user id :").strip()
    
    if not username or not user_id:
        print("[!] Username and ID cannot be empty.")
        return

    user = User(user_id,username)
    #update
    write_out_user_information(user)

def remove_user():
    #remove user
    print("\nTo Remove Please Enter:")
    username = input("username:").strip()
    user_id = input("user id :").strip()
    
    #look for
    user = load_back_user_information(user_id)
    if user is None:
        print(f"[!] No user found with ID '{user_id}'.")
        return
    
    confirm = input(f"  Remove user '{user.user_name}' (ID: {user_id})? (y/n): ").strip().lower()
    if confirm != "y":
        print("[i] Cancelled.")
        return
    
    #update 
    delete_user_from_file(user_id)
    records = load_data_from_json("resource_permission.json")
    for i in records:
        i["permission"].pop(user_id,None)
    save_data_to_json("resource_permission.json", records)

def add_new_resource():
    print("\nTo Add Please Enter:")
    
    owner_id = input("owner_id:").strip()
    owner_name = input("owner_name:").strip()
    resource_name = input("resource_name:").strip()
    
    #check
    if not owner_id or not owner_name or not resource_name:
        print("[!] All fields are required.")
        return
    
    if load_back_resource_permission(resource_name):
        print(f"[i] Resource '{resource_name}' already exists.")
        return

    #update
    file = Resource(owner_id,owner_name,resource_name)
    write_out_resource_permission(file)
    print(f"[+] Resource '{resource_name}' created with (owner: {owner_name})")

def remove_resource():
    #remove user
    print("\nTo Remove Please Enter:")
    resource_name = input("Resource name:").strip()
    
    #look for
    resource = load_back_resource_permission(resource_name)
    if resource is None:
        print(f"[!] Resoruce '{resource_name}' not found")
        return
    
    confirm = input(f"  Remove resource '{resource_name}' (owner: {resource.owner_name})? (y/n): ").strip().lower()
    if confirm != "y":
        print("[i] Cancelled.")
        return
    
    #update 
    delete_resource_from_file(resource_name)
    print(f"[-] Resource '{resource_name}' removed.")


def grant_permission():
    print("\nGrant new permission:")
    
    #what is the resource
    resource_name = input("Resource name:").strip()
    resource_information = load_back_resource_permission(resource_name)

    if resource_information is None:
        print(f"[!] Resource: '{resource_name}' not found.")
        return

    owner_id = resource_information.owner_id
    owner_name = resource_information.owner_name
    # check owner
    print("\n The following is verification process")
    answer_owner_id = input("Owner ID:").strip()
    answer_owner_name = input("Owner Name:").strip()

    if answer_owner_id == Master_key or (owner_id == answer_owner_id and owner_name == answer_owner_name):
        #grant permission
        owner = User(owner_id,owner_name)
        username = input("granted username:")
        username_id = input("granted user id :")
        
        granted_user = User(username_id,username)
        granted_permission = input("Granted Permission(read/write/execute):").strip().lower()

        #update
        Resource.grant_permission(resource_information, owner, granted_user, granted_permission)
        #print("Loaded:", resource_information.resource_name, resource_information.permission)
    else:
       print("[!!] You have no permission")
       print("[!!] Revoked")
        
def remove_permission():
    print("\nRemove permission:")
    #what is the resource
    resource_name = input("Resource name:").strip()
    resource_information = load_back_resource_permission(resource_name)

    if resource_information is None:
        print(f"[!] Resource: '{resource_name}' not found.")
        return

    owner_id = resource_information.owner_id
    owner_name = resource_information.owner_name
    
    # check owner
    print("\n The following is verification process")
    answer_owner_id = input("Owner ID:").strip()
    answer_owner_name = input("Owner Name:").strip()

    if answer_owner_id == Master_key or (owner_id == answer_owner_id and owner_name == answer_owner_name):
        #grant permission
        owner = User(owner_id,owner_name)
        username = input("Removed username:")
        username_id = input("Removed user id :")
        removed_user = User(username_id,username)
        removed_permission = input("removed_permission(read/write/execute):").strip().lower()
        
        #update
        Resource.remove_permission(resource_information, owner, removed_user, removed_permission)
        #print("Loaded:", resource_information.resource_name, resource_information.permission)
    else:
       print("[!!] You have no permission")
       print("[!!] Revoked")


ACTIONS = {
    "1":  add_new_user,
    "2":  remove_user,
    "3":  add_new_resource,
    "4":  remove_resource,
    "5":  grant_permission,
    "6":  remove_permission
}
   

# ACTIONS = {
#     "1":  add_new_user,
#     "2":  remove_user,
#     "3":  "list_users",
#     "4":  add_new_resource,
#     "5":  remove_resource,
#     "6":  "list_resources",
#     "7":  grant_permission,
#     "8":  remove_permission,
#     "9":  "check_permission",
#     "10": "list_resource_permissions",
# }
   
option = {
    "1":  'add_new_user',
    "2":  "remove_user",
    "3":  "add_new_resource",
    "4":  "remove_resource",
    "5":  "grant_permission",
    "6":  "remove_permission"
}

# option = {
#     "1":  'add_new_user',
#     "2":  "remove_user",
#     "3":  "list_users",
#     "4":  "add_new_resource",
#     "5":  "remove_resource",
#     "6":  "list_resources",
#     "7":  "grant_permission",
#     "8":  "remove_permission",
#     "9":  "check_permission",
#     "10": "list_resource_permissions",
# }




def main():
    while True:
        print("Welcome\n")
        print("Here is a list of options")
        for i in option:
            print(f'{i}: {option[i]}')
        print("\n[i] To Exit, Enter 0")
        action =  input("Select an option: ").strip()

        if action == "0":
            print("Exiting...")
            print('Please wait')
            # time.sleep(1)
            print("Exited")
            break
        elif action in ACTIONS:
            try:
                ACTIONS[action]()
            
            except TypeError:
                print("Placeholder")

        input("\nPress Enter to return to the menu...")
    


   
main()