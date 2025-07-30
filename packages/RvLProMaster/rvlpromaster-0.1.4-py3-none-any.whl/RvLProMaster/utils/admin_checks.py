from .create_log import CreateLog
import glob
import os

class adminUtils:
  def __init__(self):
    self.CheckAdmin = self.checkAdmin()
    
  def FindAdminList(self, dir="."):
      for find_env in glob.iglob(f"{dir}/**/admin.txt", recursive=True):
          if find_env is not None:
              result = os.path.abspath(find_env)
              return str(result)
      else:
          CreateLog("INFO", "Admin List Not Found Creating New Admin List")
          new_file_path = os.path.join(dir, "admin.txt")
          new_user_id = int(input(f"Enter Your First User ID: "))
          with open(new_file_path, 'w') as file:
              file.write(str(new_user_id))
          CreateLog("INFO", f"New Admin List Created")
          return new_file_path

    
  # Check admin
  def checkAdmin(self):
    """Check if the user in List admin or not"""
    with open(self.FindAdminList(), "r") as f:
      match_admin = [int(line.strip()) for line in f.readlines()]
      return match_admin
  
  # Add admin
  def AddAdmin(self, user_id: int):
    """Add user to admin list"""
    with open(self.FindAdminList(), "a") as f:
      f.write(f"\n{user_id}")
      CreateLog("INFO", f"User ID {user_id} Added To Admin List")
  
  # Remove admin
  def RemoveAdmin(self, user_id: int):
    """Remove a user from the admin list."""
    with open(self.FindAdminList(), "r") as r:
      read_admin = [line.strip() for line in r if line.strip()]
      
      if str(user_id) in read_admin:
          CreateLog("INFO", f"User ID {user_id} Deleted From Admin List")
          read_admin.remove(str(user_id))
          
          with open(self.FindAdminList(), "w") as w:
            if read_admin:
              w.write("\n".join(read_admin))
            else:
              w.write("")
      else:
          CreateLog("INFO", f"User ID {user_id} Not Found In Admin List")
      
AdminUtils = adminUtils()
CheckAdmin = AdminUtils.CheckAdmin