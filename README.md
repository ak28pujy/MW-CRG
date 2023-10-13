# MW-CRG
## Table of Contents
- [Introduction](https://github.com/ak28pujy/MW-CRG#introduction)
- [Requirements](https://github.com/ak28pujy/MW-CRG#requirements)
- [Download and Setup](https://github.com/ak28pujy/MW-CRG#download-and-setup)
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
- [Files in this project](https://github.com/ak28pujy/MW-CRG#files-in-this-project)
## Introduction
This project is a comprehensive tool for automatic data collection and analysis for businesses. It combines web scraping, Google search, RSS feed analysis and the OpenAI API to collect relevant information about a given company.

With the integrated GUI application, users can set specific search criteria and preferences to start the data extraction process. The collected data is analyzed and can be output in both text and PDF formats.

The tool is especially useful for market analysts, researchers and anyone who needs a quick overview of a company and its activities on the web without having to manually browse through countless pages.
## Requirements
To run this tool successfully, make sure that you meet the following requirements:
1. Operating system (OS):
   - Windows 10 or newer (x86_64/AMD64).
   - macOS 13 or newer (x86_64/AMD64 or ARM).
        - Installable and usable, but not fully functional currently.
3. Browser: Firefox or Chrome (latest version).
4. Python version 3.11.6: Can be downloaded [here](https://www.python.org/downloads/release/python-3116/) at the bottom of the page.
   - Probably older Python version will work too (Please do not use newest Python version 3.12 at the moment).
   - Usually Python is preinstalled on macOS.
   - Make sure that Python is set as system environment variable under Windows.
6. OpenAI API Key: Can be created [here](https://platform.openai.com/account/api-keys).
7. Google Custom Search JSON API Keys: See documentation [here](https://developers.google.com/custom-search/v1/overview?hl=en).
## Download and Setup
### Windows
#### Option 1 (Recommended)
1. Click [here](https://github.com/ak28pujy/MW-CRG/archive/refs/heads/main.zip) to download the project.
2. Extract the zip-file into a folder.
3. Click [here](https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe) to download Python version 3.11.6.
    1. If Python is not yet installed:
       1. Double click on ```python-3.11.6-amd64.exe```.
       2. Check the box ```Add python.exe to PATH```.
       3. Click on ```Install Now```.
       4. Wait until the installation is finished and click ```Close```.
    2. If Python is already installed:
       1. Double click on ```python-3.11.6-amd64.exe```.
       2. Click on ```Customize installation``` or ```Modify```.
       3. Make sure that there is a check mark everywhere under ```Optional Features```.
       4. Click on ```Next```.
       5. Check the box ```Add Python to environment variables```.
       6. Click on ```Install```.
       7. Wait until the installation is finished and click ```Close```.
4. Navigate to the directory where you downloaded the project.
5. Open the folder ```setup```.
6. Right-click on ```install.bat``` and select ```Run as administrator```.
7. When Windows Smartscreen pops up, click on ```More info``` and then on ```Run anyway```. (More information about Microsoft Defender SmartScreen [here](https://learn.microsoft.com/en-us/windows/security/operating-system-security/virus-and-threat-protection/microsoft-defender-smartscreen/))
8. Press the ```1``` key and then press the ```Enter``` key.
9. Wait for the dependencies to be installed.
10. Follow the instructions in the script.
11. If you have launched the app directly, make sure that the correct API keys are set. These can be changed under Menu and then Settings.
#### Option 2
1. Click [here](https://github.com/ak28pujy/MW-CRG/archive/refs/heads/main.zip) to download the project.
2. Extract the zip-file into a folder.
3. Click [here](https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe) to download Python version 3.11.6.
    1. If Python is not yet installed:
       1. Double click on ```python-3.11.6-amd64.exe```.
       2. Check the box ```Add python.exe to PATH```.
       3. Click on ```Install Now```.
       4. Wait until the installation is finished and click ```Close```.
    2. If Python is already installed:
       1. Double click on ```python-3.11.6-amd64.exe```.
       2. Click on ```Customize installation``` or ```Modify```.
       3. Make sure that there is a check mark everywhere under ```Optional Features```.
       4. Click on ```Next```.
       5. Check the box ```Add Python to environment variables```.
       6. Click on ```Install```.
       7. Wait until the installation is finished and click ```Close```.
4. Start PowerShell as administrator:
     1. Press the ```Windows``` key.
     2. Type ```PowerShell```.
     3. Right-click on ```Windows PowerShell``` and select ```Run as administrator```.
5. execute the following command:
```
Set-ExecutionPolicy RemoteSigned
```
4. You will probably be prompted for confirmation. Please accept and close the PowerShell.
5. Navigate to the directory where you downloaded the project.
6. Right-click, select ```Open in Terminal``` and enter:
```
python -m venv venv
```
```
.\venv\Scripts\activate
```
7. Install the required packages with:
```
pip install -r requirements.txt
```
```
deactivate
```
### macOS
#### Option 1 (Recommended)
1. Click [here](https://github.com/ak28pujy/MW-CRG/archive/refs/heads/main.zip) to download the project.
2. Open a terminal window.
3. Navigate to the folder ```setup``` (E.g. ```cd downloads/mw-crg-main/setup```), make the script executable (```chmod 755 install.sh```) and run install.sh (```./install.sh```). See documentation [here](https://support.apple.com/guide/terminal/apdd100908f-06b3-4e63-8a87-32e71241bab4/mac) for more information.
4. Press the ```1``` key and then press the ```Enter``` key.
5. Wait for the dependencies to be installed.
6. Follow the instructions in the script.
7. If you have launched the app directly, make sure that the correct API keys are set. These can be changed under Menu and then Settings.
#### Option 2
1. Click [here](https://github.com/ak28pujy/MW-CRG/archive/refs/heads/main.zip) to download the project.
2. Open a terminal window.
3. Navigate to the directory where you downloaded the project (E.g. ```cd downloads/mw-crg-main```) and enter:
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
1. Navigate to the directory where you downloaded the project.
2. Open the folder ```start```.
3. Double click on ```run.vbs```.
4. Make sure that the correct API keys are set. These can be changed under Menu and then Settings.
#### Option 2
1. Navigate to the directory where you downloaded the project.
2. Right-click, select ```Open in Terminal``` and enter:
```
.\venv\Scripts\activate
```
```
python app.py
```
3. Make sure that the correct API keys are set. These can be changed under Menu and then Settings.
### macOS
#### Option 1 (Recommended)
1. Navigate to the directory where you downloaded the project.
2. Open the folder ```start```.
3. Double click on ```run.scpt```.
4. Press the gray ```Play``` button in the upper right corner of the Script Editor.
5. Make sure that the correct API keys are set. These can be changed under Menu and then Settings.
#### Option 2
1. Open a terminal window.
2. Navigate to the directory where you downloaded the project (E.g. ```cd downloads/mw-crg-main```) and enter:
```
source venv/bin/activate
```
```
python app.py
```
3. Make sure that the correct API keys are set. These can be changed under Menu and then Settings.
## Files in this project
main.py: Main script that drives data collection, analysis and reporting. It uses both the Google API and the OpenAI API to collect relevant information about a given company and generate a summary report.

app.py: A GUI application created with PyQt6. Allows users to enter various settings and search criteria and start the extraction process.

counttokens.py: Helper functions for counting tokens in a given message or list of messages, useful for working with the OpenAI API.

openai_prompt.py: Provides functions to interact with the OpenAI API. Specializes in extracting and summarizing content from URLs using the OpenAI API.

output.py: Contains functions for generating and saving output in various formats (TXT, PDF, DOCX). Uses specific libraries for creating documents.

requirements.txt: Lists all the dependencies of the project. To install all the required packages, run: ```pip install -r requirements.txt```

.env: Contains environment variables for API keys (OpenAI and Google) and last search settings. Additionally, it offers miscellaneous settings such as task concurrency and page load timeouts. Ensure to replace XXXXXX placeholders with actual values.

[Geckodriver](https://github.com/mozilla/geckodriver): Version 0.33.0

[ChromeDriver](https://chromedriver.chromium.org): Version 118.0.5993.70
