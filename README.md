## Pre-rerequisite
Python3

### Steps to setup:
1. Create a Virtual Environment:
`python3 -m venv venv`

1. Activate the Virtual Environment:
    1. Linux/macOS:
`source venv/bin/activate`
    1. Windows:
`venv\Scripts\activate`

1. Install Dependencies
`pip3 install -r requirements.txt`


1. Download the ChromeDriver that fits the system
`python3 ./scripts/download_latest_chromedriver.py`

1. Run the tanka generator
`python3 ./src/main.py`
