import sys

import requests
import argparse
import os
import shutil
from string import Template
from .helper import get_latest_nvda_version, install

script_path = os.path.dirname(os.path.abspath(__file__))
context: dict = {}

def rename_addon_folder(global_plugins_path):
	for item in os.listdir(global_plugins_path):
		if "$" in item:  # This checks for folder like $mylib
			old_path = os.path.join(global_plugins_path, item)
			new_path = os.path.join(global_plugins_path, context["addon_name"])
			os.rename(old_path, new_path)
			return new_path  # Return the new path for further formatting
	return None

def format_file(file: str):
	with open(file, "r", encoding="utf-8") as f:
		content = f.read()
		template = Template(content)
		new_content = template.safe_substitute(context)
	with open(file, "w", encoding="utf-8") as f1:
		f1.write(new_content)

def copy_template(destination_path: str):
	shutil.copytree(os.path.abspath(os.path.join(script_path, "template")), destination_path)
	for dirpath, _, filenames in os.walk(destination_path):
		for filename in filenames:
			if filename.endswith(".py"):
				file = os.path.join(dirpath, filename)
				format_file(file)

def to_safe_name(name: str):
	return name.replace(" ", "_")

def input_or_arg(name_arg):
	if not name_arg:
		name = input("Folder name for the addon:")
	else:
		name = name_arg
	return to_safe_name(name)

def set_context():
	global context
	print("Please enter addon details.")
	addon_name = input("Displayed addon name:")
	context = {
		"addon_name": addon_name,
		"addon_description": input("description:"),
		"version": input("version:"),
		"username": input("author name:"),
		"addon_minimumNVDAVersion": input("minimumNVDAVersion:"),
		"addon_lastTestedNVDAVersion": get_latest_nvda_version(),
	}

def initialize_git(path: str):
	os.system(f'git init "{path}"')

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("name", nargs="?", help="Folder name for the new addon")
	parser.add_argument("package", nargs="?", help="Package name if using 'add'")
	args = parser.parse_args()
	if args.name =="add" and args.package:
		install(args.package)
		sys.exit(0)

	folder_name = input_or_arg(args.name)
	destination = os.path.abspath(os.path.join(os.getcwd(), folder_name))
	set_context()
	copy_template(destination)
	with open(f"{folder_name}/addon_name.txt", "w") as file:
		file.write(folder_name)
	rename_addon_folder(os.path.join(destination, "addon", "globalPlugins"))
	if input("Initialize git repository? [y/n]:").strip().lower().startswith("y"):
		initialize_git(destination)
	print(f"Addon created at: {destination}")

if __name__ == "__main__":
	main()
