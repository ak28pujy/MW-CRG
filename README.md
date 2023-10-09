# MW-CRG
## Table of Contents
- [Introduction](https://github.com/ak28pujy/MW-CRG#introduction)
- [Requirements](https://github.com/ak28pujy/MW-CRG#requirements)
- [Download](https://github.com/ak28pujy/MW-CRG#download)
    - [Download with Git](https://github.com/ak28pujy/MW-CRG#download-with-git)
    - [Download without Git](https://github.com/ak28pujy/MW-CRG#download-without-git)
- [Setup](https://github.com/ak28pujy/MW-CRG#setup)
    - [Windows](https://github.com/ak28pujy/MW-CRG#windows)
        - [Option 1 (Recommended)](https://github.com/ak28pujy/MW-CRG#option-1-recommended)
        - [Option 2](https://github.com/ak28pujy/MW-CRG#option-2)
    - [macOS](https://github.com/ak28pujy/MW-CRG#macos)
        - [Option 1 (Recommended)](https://github.com/ak28pujy/MW-CRG#option-1-recommended-1)
        - [Option 2](https://github.com/ak28pujy/MW-CRG#option-2-1)
- [Usage](https://github.com/ak28pujy/MW-CRG#usage)
    - [Windows](https://github.com/ak28pujy/MW-CRG#windows-1)
        - [Option 1 (Recommended)](https://github.com/ak28pujy/MW-CRG#option-1-recommended-2)
        - [Option 2](https://github.com/ak28pujy/MW-CRG#option-2-2)
    - [macOS](https://github.com/ak28pujy/MW-CRG#macos-1)
        - [Option 1 (Recommended)](https://github.com/ak28pujy/MW-CRG#option-1-recommended-3)
        - [Option 2](https://github.com/ak28pujy/MW-CRG#option-2-3)
- [Files in the repository](https://github.com/ak28pujy/MW-CRG#files-in-the-repository)
## Introduction
This project is a comprehensive tool for automatic data collection and analysis for businesses. It combines web scraping, Google search, RSS feed analysis and the OpenAI API to collect relevant information about a given company.

With the integrated GUI application, users can set specific search criteria and preferences to start the data extraction process. The collected data is analyzed and can be output in both text and PDF formats.

The tool is especially useful for market analysts, researchers and anyone who needs a quick overview of a company and its activities on the web without having to manually browse through countless pages.
## Requirements
To run this tool successfully, make sure that you meet the following requirements:
1. Operating system (OS):
   - Windows 11 (x86_64/AMD64)
   - macOS Version 13 or newer (x86_64/AMD64 or ARM)
3. Browser: Firefox or Chrome (latest version)
4. Python Version 3.11 or newer: Can be downloaded [here](https://www.python.org/downloads/)
5. OpenAI API Key: Can be created [here](https://platform.openai.com/account/api-keys)
6. Google Custom Search JSON API Keys: See documentation [here](https://developers.google.com/custom-search/v1/overview?hl=en)
## Download
### Download with Git
1. Make sure you have [Git](https://git-scm.com/downloads) installed for your OS.
2. Clone the repository with: ```git clone https://github.com/ak28pujy/MW-CRG.git```
### Download without Git
1. Click on the green "Code" button above and then on "Download ZIP".
2. Extract the zip-file into a folder.
## Setup
### Windows
#### Option 1 (Recommended)
1. Navigate to the directory where you downloaded the repository.
2. Open the folder ```setup```.
3. Right-click on ```install.bat``` and select "Run as administrator".
4. Follow the instructions in the script.
#### Option 2
1. Start PowerShell as administrator:
     1. Press the Windows key
     2. Type "PowerShell"
     3. Right-click on "Windows PowerShell" and select "Run as administrator"
2. execute the following command:
```
Set-ExecutionPolicy RemoteSigned
```
3. You will probably be prompted for confirmation. Please accept and close the PowerShell.
4. Navigate to the directory where you downloaded the repository.
5. Right-click, select "Open in Terminal" and enter:
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
```
deactivate
```
### macOS
#### Option 1 (Recommended)
1. Open a terminal window.
2. Navigate to the folder ```setup``` (E.g. ```cd downloads/mw-crg-main/setup```), make the script executable (```chmod 755 install.sh```) and run install.sh (```./install.sh```). See documentation [here](https://support.apple.com/guide/terminal/apdd100908f-06b3-4e63-8a87-32e71241bab4/mac) for more information.
3. Follow the instructions in the script.
#### Option 2
1. Open a terminal window.
2. Navigate to the directory where you downloaded the repository (E.g. ```cd downloads/mw-crg-main```) and enter:
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
```
deactivate
```
4. Change the permission for the drivers:
```
find ./driver/mac/ -type f -exec chmod +x {} \;
```
```
find ./driver/mac/ -type f -exec xattr -d com.apple.quarantine {} \;
```
## Usage
### Windows
#### Option 1 (Recommended)
1. Navigate to the directory where you downloaded the repository.
2. Open the folder ```start```.
3. Double click on ```run.vbs```.
4. Make sure that the correct API keys are set. These can be changed under Menu and then Settings.
#### Option 2
1. Navigate to the directory where you downloaded the repository.
2. Right-click, select "Open in Terminal" and enter:
```
.\venv\Scripts\activate
```
```
python app.py
```
3. Make sure that the correct API keys are set. These can be changed under Menu and then Settings.
### macOS
#### Option 1 (Recommended)
1. Navigate to the directory where you downloaded the repository.
2. Open the folder ```start```.
3. Double click on ```run.scpt```.
4. Press the gray "Play" button in the upper right corner of the Script Editor.
5. Make sure that the correct API keys are set. These can be changed under Menu and then Settings.
#### Option 2
1. Open a terminal window.
2. Navigate to the directory where you downloaded the repository (E.g. ```cd downloads/mw-crg-main```) and enter:
```
source venv/bin/activate
```
```
python app.py
```
3. Make sure that the correct API keys are set. These can be changed under Menu and then Settings.
## Files in the repository
main.py: Main script that drives data collection, analysis and reporting. It uses both the Google API and the OpenAI API to collect relevant information about a given company and generate a summary report.

app.py: A GUI application created with PyQt6. Allows users to enter various settings and search criteria and start the extraction process.

counttokens.py: Helper functions for counting tokens in a given message or list of messages, useful for working with the OpenAI API.

openai_prompt.py: Provides functions to interact with the OpenAI API. Specializes in extracting and summarizing content from URLs using the OpenAI API.

output.py: Contains functions for generating and saving output in various formats (TXT, PDF, DOCX). Uses specific libraries for creating documents.

requirements.txt: Lists all the dependencies of the project. To install all the required packages, run: ```pip install -r requirements.txt```

.env: Contains environment variables for API keys (OpenAI and Google) and last search settings. Additionally, it offers miscellaneous settings such as task concurrency and page load timeouts. Ensure to replace XXXXXX placeholders with actual values.

[Geckodriver](https://github.com/mozilla/geckodriver): Version 0.33.0

[ChromeDriver](https://chromedriver.chromium.org): Version 117.0.5938.149
