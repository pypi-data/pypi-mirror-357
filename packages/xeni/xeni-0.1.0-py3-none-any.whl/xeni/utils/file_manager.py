import os
import platform

from xeni.utils.config import AGENT_CONFIG_FILENAMES

class ConfigFinder():
    def __init__(self, agentName):
        self.fileName = AGENT_CONFIG_FILENAMES[agentName]
        self.agentName = agentName

    def get_path(self):
        """Searches normal locations for the config file"""

        potential_paths = []
        config_filename = self.fileName
        config_folder = f"{self.agentName[0].upper()}{self.agentName[1:]}"

        # Get the OS name
        system = platform.system().lower()

        if system == "windows":
            # windows paths
            appdata = os.environ.get('APPDATA', '')
            localappdata = os.environ.get('LOCALAPPDATA', '')
            userprofile = os.environ.get('USERPROFILE', '')
            

            potential_paths = [
                os.path.join(appdata, config_folder, config_filename),
                os.path.join(localappdata, config_folder, config_filename),
                os.path.join(userprofile, "AppData", "Roaming", config_folder, config_filename),
                os.path.join(userprofile, "AppData", "Local", config_folder, config_filename),
                os.path.join(userprofile, f".{self.agentName}", config_filename),
                os.path.join(userprofile, config_filename),
            ]
        elif system == "darwin":
            # macOS paths
            home = os.path.expanduser("~")
            
            potential_paths = [
                os.path.join(home, "Library", "Application Support", config_folder, config_filename),
                os.path.join(home, "Library", "Preferences", config_folder, config_filename),
                os.path.join(home, ".claude", config_filename),
                os.path.join(home, ".config", self.agentName, config_filename),
                os.path.join(home, config_filename),
            ]
        elif system == "linux":
            # Linux paths
            home = os.path.expanduser("~")
            xdg_config = os.environ.get('XDG_CONFIG_HOME', os.path.join(home, '.config'))
            
            potential_paths = [
                os.path.join(xdg_config, self.agentName, config_filename),
                os.path.join(home, f".{self.agentName}", config_filename),
                os.path.join(home, ".config", self.agentName, config_filename),
                os.path.join(home, config_filename),
                os.path.join("/etc", self.agentName, config_filename),
            ]
    
        # Search in potential paths
        found_path = ""
        
        print("Checking potential locations:")
        for path in potential_paths:
            print(f"  Checking: {path}")
            if os.path.exists(path) and os.path.isfile(path):
                abs_path = os.path.abspath(path)
                found_path = abs_path
                if system == "windows":
                    found_path = found_path.replace("\\", "\\\\")                   
                print(f"    ✓ FOUND: {abs_path}")
                break
            else:
                print(f"    ✗ Not found")
        
        return found_path
    
    def system_search(self):
        """
        Search the entire file system for the config file (more thorough but slower)
        """
        filename = self.fileName

        print(f"\nPerforming system-wide search for {filename}...")
        print("⚠️  This may take a while...")
        print("-" * 50)
        
        found_file = ""
        
        # Get the OS name
        system = platform.system().lower()
        
        # Getting OS specific search roots to look through
        if system == "windows":
            search_roots = [
                os.environ.get('SYSTEMDRIVE', 'C:') + os.sep,
                os.environ.get('USERPROFILE', ''),
            ]
        else:
            search_roots = [
                os.path.expanduser("~"),  # User home directory
                "/usr",
                "/opt",
                "/etc",
            ]
        
        for root in search_roots:
            if not os.path.exists(root):
                continue
                
            print(f"Searching in: {root}")
            
            try:
                for dirpath, dirnames, filenames in os.walk(root):
                    # Skip hidden and system directories for efficiency
                    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in ['System Volume Information', '$Recycle.Bin']]
                    
                    if filename in filenames:
                        full_path = os.path.abspath(os.path.join(dirpath, filename))
                        found_file = full_path
                        print(f"  ✓ FOUND: {full_path}")
                        break
                        
            except (PermissionError, OSError) as e:
                print(f"  ⚠️  Skipped {root}: {e}")
                continue
        
        return found_file
