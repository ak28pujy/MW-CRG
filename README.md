# MW-CRG
This project is a comprehensive tool for automatic data collection and analysis for businesses. It combines web scraping, Google search, RSS feed analysis and the OpenAI API to collect relevant information about a given company.

With the integrated GUI application, users can set specific search criteria and preferences to start the data extraction process. The collected data is analyzed and can be output in both text and PDF formats.

The tool is especially useful for market analysts, researchers and anyone who needs a quick overview of a company and its activities on the web without having to manually browse through countless pages.
## Requirements
To run this tool successfully, make sure that you meet the following requirements:

1. Operating system (OS):
  - Windows (x86_64/AMD64)
  - Linux (x86_64/AMD64)
  - MacOS (x86_64/AMD64 or ARM)
2. Browser: Firefox or Chrome (latest version)
3. Python Version 3.11 or newer: Can be downloaded [here](https://www.python.org/downloads/)
4. OpenAI API Key: Can be created [here](https://platform.openai.com/account/api-keys)
5. Google Custom Search JSON API Keys: See documentation [here](https://developers.google.com/custom-search/v1/overview?hl=en)

## Download
### Download with Git
1. Make sure you have [Git](https://git-scm.com/downloads) installed for your OS.
2. Clone the repository with: ```git clone https://github.com/ak28pujy/MW-CRG.git```
### Download without Git
1. Click on the green "Code" button and then on "Download ZIP".
2. Extract the zip-file into a folder.
## Setup
### Windows
1. Start PowerShell as administrator:
     1. Press the Windows key
     2. Type "PowerShell"
     3. Right-click on "Windows PowerShell" and select "Run as administrator"
2. execute the following command:
```
Set-ExecutionPolicy RemoteSigned
```
3. You will probably be prompted for confirmation. Please accept and close the powershell.
4. Navigate to the directory where you downloaded the repository.
5. Open a CMD, Bash, or Powershell window in the directory and enter:
```
python -m venv venv
```
```
.\venv\Scripts\activate
```
6. Install the required packages with:
```
pip install -r requirements.txt
```
### macOS and Linux
1. Navigate to the directory where you downloaded the repository.
2. Open a CMD, Bash, or Powershell window in the directory and enter:
```
python -m venv venv
```
```
source venv/bin/activate
```
3. Install the required packages with:
```
pip install -r requirements.txt
```
## Usage
1. Navigate to the directory where you downloaded the repository.
2. Open a CMD, Bash, or Powershell window in the directory and enter:
    1. Windows: ```.\venv\Scripts\activate```, macOS and Linux: ```source venv/bin/activate```
    2. ```python app.py```
3. Make sure that the correct API keys are set. These can be changed under Menu and then Settings.
## Files in the repository
main.py: Main script that drives data collection, analysis and reporting. It uses both the Google API and the OpenAI API to collect relevant information about a given company and generate a summary report.

app.py: A GUI application created with PyQt6. Allows users to enter various settings and search criteria and start the extraction process.

counttokens.py: Helper functions for counting tokens in a given message or list of messages, useful for working with the OpenAI API.

requirements.txt: Lists all the dependencies of the project. To install all the required packages, run: ```pip install -r requirements.txt```

[Geckodriver](https://github.com/mozilla/geckodriver): Version 0.33.0

[ChromeDriver](https://chromedriver.chromium.org): Version 117.0.5938.88
