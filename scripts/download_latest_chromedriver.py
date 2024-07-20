import requests
import json
import platform
import zipfile
import os
import stat

# Get the latest version of ChromeDriver
url = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json'
response = requests.get(url)
data = json.loads(response.text)

latest_version = data['channels']['Stable']['version']
print(f"Latest ChromeDriver version: {latest_version}")

# Determine the correct download URL based on the operating system
system = platform.system().lower()
if system == "linux":
    os_name = "linux64"
elif system == "darwin":
    os_name = "mac-x64"  # or "mac-arm64" for Apple Silicon
elif system == "windows":
    os_name = "win32"
else:
    raise Exception("Unsupported operating system")

download_url = None
for item in data['channels']['Stable']['downloads']['chromedriver']:
    if item['platform'] == os_name:
        download_url = item['url']
        break

if not download_url:
    raise Exception(f"Unable to find ChromeDriver download for {os_name}")

# Download the ChromeDriver zip file
response = requests.get(download_url)
zip_file_name = "chromedriver.zip"
with open(zip_file_name, "wb") as file:
    file.write(response.content)

# Extract the zip file
with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
    zip_ref.extractall()

# Remove the zip file
os.remove(zip_file_name)

print(f"ChromeDriver {latest_version} has been downloaded and extracted.")

# Determine the path to the chromedriver executable
if system == "windows":
    chromedriver_path = "./chromedriver-win32/chromedriver.exe"
else:
    chromedriver_path = "./chromedriver-" + os_name + "/chromedriver"

# Set executable permissions
st = os.stat(chromedriver_path)
os.chmod(chromedriver_path, st.st_mode | stat.S_IEXEC)

print(f"Permissions updated for ChromeDriver at {chromedriver_path}")
