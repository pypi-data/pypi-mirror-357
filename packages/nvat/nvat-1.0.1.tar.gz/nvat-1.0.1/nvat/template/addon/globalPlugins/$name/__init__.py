# Import necessary NVDA modules
import os
import sys
import globalPluginHandler  # Base class for global plugins
import ui  # NVDA's built-in UI message functions like speech and braille

# Add the current folder to Python's path, so modules in this folder can be imported easily
sys.path.append(os.path.dirname(__file__))


# GlobalPlugin is a special class NVDA looks for.
# It runs automatically when NVDA starts (if the addon is enabled).
class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	# This is a script function. It will be triggered when the user presses a defined gesture (hotkey).
	def script_hello(self, gesture):
		"""
		Displays a simple message when the user presses NVDA+H.
		You can replace "hello!" with anything else.
		"""
		ui.message("hello!")  # This will be spoken and shown on the braille display if available

	# Define keyboard gestures and map them to the script functions above.
	# Format: "kb:KEY_COMBINATION": "function_name_without_script_"
	__gestures = {
		"kb:NVDA+H": "hello"  # When NVDA+H is pressed, it runs script_hello()
	}
