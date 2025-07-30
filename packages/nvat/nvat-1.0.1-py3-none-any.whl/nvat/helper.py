import os
import sys
import time

import requests
import subprocess

def get_latest_nvda_version():
	try:
		response = requests.get("https://github.com/nvaccess/nvda/releases/latest", allow_redirects=False)
		if "Location" in response.headers:
			latest_url = response.headers["Location"]
			version = latest_url.strip("/").split("/")[-1].strip("-").split("-")[-1]
			return version
	except Exception:
		print(Exception)
		return None

def install(pkg: str):
	if not os.path.exists("addon_name.txt"):
		print("Invalid NVDA addon project you need to run from a project")
		return sys.exit(1)
	addonName = ""
	with open("addon_name.txt", "r") as file:
		addonName = file.read()
	if os.path.exists(f"./addon/globalPlugins/{addonName}"):
		os.chdir(f"./addon/globalPlugins/{addonName}")
		try:
			print(f"🔄 Installing '{pkg}...")
			install_time_start = time.time()
			subprocess.run([
				"pip", "install", pkg,
				"--target", pkg, "--no-warn-script-location"
				], check=True)
			install_time_stop = time.time()
			print(f"✅ Package '{pkg}' installed successfully in {install_time_stop - install_time_start:.2f} seconds.")
		except subprocess.CalledProcessError as e:
			print(f"pip error! {e}")
	else:
		print("Invalid NVDA addon structure. This tool must be run from the root folder of your addon project, not from inside subfolders like 'globalPlugins'.")
		sys.exit(1)

