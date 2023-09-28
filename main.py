import asyncio
import os
import platform
import re
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

import feedparser
import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.wait import WebDriverWait

import counttokens
import openai_prompt
import output

OPENAI_API_KEY = 'OPENAI_API_KEY'
GOOGLE_API_KEY = 'GOOGLE_API_KEY'
GOOGLE_CSE_ID = 'GOOGLE_CSE_ID'
MAX_CONCURRENT_TASKS = 'MAX_CONCURRENT_TASKS'
MAX_CONCURRENT_URLS = 'MAX_CONCURRENT_URLS'
PAGE_LOAD_TIMEOUT = 'PAGE_LOAD_TIMEOUT'

DRIVERS_PATH = './driver/'

load_dotenv()
openai.api_key = os.getenv(OPENAI_API_KEY)
google_api_key = os.getenv(GOOGLE_API_KEY)
google_cse_id = os.getenv(GOOGLE_CSE_ID)
semaphore = asyncio.Semaphore(int(os.getenv(MAX_CONCURRENT_TASKS, 2)))
max_concurrent_urls = int(os.getenv(MAX_CONCURRENT_URLS, 5))
page_load_timeout = int(os.getenv(PAGE_LOAD_TIMEOUT, 10))


async def limited_execute(task, *args):
    async with semaphore:
        return await task(*args)


def get_system_info():
    print('OS:', platform.system())
    print('Architecture:', platform.machine())


def validate_inputs(company, model, language, num_urls_google_search, num_urls_google_news):
    if not (company and model and language):
        print(f"\nInvalid input. Please check the parameters.")
        return False
    if num_urls_google_search > 10:
        print(f"\nInvalid input. Number of URLs from Google Search must not be higher than 10.")
        return False
    if num_urls_google_news > 15:
        print(f"\nInvalid input. Number of URLs from Google News must not be higher than 15.")
        return False
    return True


def get_driver_path(driver_name):
    os_name = platform.system()
    arch = 'intel' if 'x86_64' in platform.machine() or 'AMD64' in platform.machine() else 'arm'
    os_name = 'windows' if os_name == 'Windows' else 'mac' if os_name == 'Darwin' else None
    if os_name is None:
        raise ValueError("The current operating system is not supported.")
    if os_name == 'windows' and arch == 'arm':
        raise ValueError(f"{os_name.capitalize()} ARM is not supported.")
    exe_extension = '.exe' if os_name == 'windows' else ''
    return f"{DRIVERS_PATH}{os_name}/{arch}/{driver_name}{exe_extension}"


BROWSERS = [{"driver": webdriver.Firefox, "path": get_driver_path("geckodriver"), "service": FirefoxService},
            {"driver": webdriver.Chrome, "path": get_driver_path("chromedriver"), "service": ChromeService}]


def get_browser(browser):
    if browser["driver"] == webdriver.Firefox:
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.set_preference("pdfjs.disabled", False)
        firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
        firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
        firefox_options.set_preference("browser.download.panel.shown", False)
        return browser["driver"](options=firefox_options,
                                 service=browser["service"](executable_path=browser["path"], log_output=os.devnull))
    else:
        chrome_options = webdriver.ChromeOptions()
        prefs = {"download.prompt_for_download": False, "download.directory_upgrade": True,
                 "plugins.always_open_pdf_externally": False, "download.default_directory": "/dev/null"}
        chrome_options.add_experimental_option('prefs', prefs)
        return browser["driver"](options=chrome_options, service=browser["service"](executable_path=browser["path"]))


def google_search(search_term, api_key, cse_id, **kwargs):
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, **kwargs, cr='countryDE', gl='de', hl='de').execute()
        if 'items' in res:
            return [(i['title'], i['link']) for i in res['items'] if 'title' in i and 'link' in i]
        else:
            print(f"\nNo results found for search term '{search_term}'.")
            return []
    except HttpError as e:
        print(f"\nAn HTTP error has occurred: {e}")
        return []
    except Exception as e:
        print(f"\nAn error has occurred: {e}")
        return []


def google_news_rss(search_term, num):
    try:
        url = f"https://news.google.com/rss/search?q={quote(search_term)}&hl=de&gl=DE&ceid=DE:de"
        response = requests.get(url)
        response.raise_for_status()
        feed = feedparser.parse(response.text)
        if not feed.entries:
            raise ValueError("\nNo news entries found for this search query.")
        return [(entry.title, entry.link) for entry in feed.entries[:num]]
    except requests.HTTPError as e:
        print(f"\nError accessing the URL: {e}")
        return []
    except Exception as e:
        print(f"\nAn error has occurred: {str(e)}")
        return []


async def execute_google_search(search_terms, search_func, num_results):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return {search_term: [(info, url) for info, url in await loop.run_in_executor(executor, lambda: zip(
            execute_extract_text_from_url(
                [url for _, url in search_func(search_term, google_api_key, google_cse_id, num=num_results)], BROWSERS),
            [url for _, url in search_func(search_term, google_api_key, google_cse_id, num=num_results)]))] for
                search_term in search_terms}


async def execute_google_news_rss(search_terms, search_func, num_results):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return {search_term: [(info, url) for info, url in await loop.run_in_executor(executor, lambda: zip(
            execute_extract_text_from_url([url for _, url in search_func(search_term, num=num_results)], BROWSERS),
            [url for _, url in search_func(search_term, num=num_results)]))] for search_term in search_terms}


def execute_extract_text_from_url(url_list, browsers):
    with ThreadPoolExecutor(max_workers=max_concurrent_urls) as executor:
        return list(executor.map(lambda url: extract_text_from_url(url, browsers), url_list))


def extract_text_from_url(url, browsers):
    for browser in browsers:
        try:
            browser = get_browser(browser)
            page_content = get_page_content(browser, url)
            if page_content:
                return page_content
        except Exception as e:
            print(f"\nError using {browser['driver'].__name__}: {e}")
    return ""


def get_page_content(browser, url):
    page_text = ""
    try:
        browser.get(url)
        WebDriverWait(browser, page_load_timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete')
        if '.google.com' in url:
            buttons_to_try = ["//*[@aria-label='Alle akzeptieren']", "//*[@aria-label='Accept all']"]
            button_clicked = False
            for button_xpath in buttons_to_try:
                try:
                    browser.find_element(By.XPATH, button_xpath).click()
                    WebDriverWait(browser, page_load_timeout).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete')
                    button_clicked = True
                    break
                except NoSuchElementException:
                    pass
            if not button_clicked:
                print("\nError clicking the accept button on Google.")
        time.sleep(5)
        page_text = BeautifulSoup(browser.page_source, 'html.parser').get_text()
    except Exception as e:
        print(f"\nError fetching the URL {url}: {e}")
    browser.quit()
    page_text = re.sub(' +', ' ', page_text)
    page_text = re.sub('\n+', '\n', page_text).strip()
    return page_text


def generate_report(info_dict, company, model, language, company_info):
    response_content, prompt, response = openai_prompt.summarize(info_dict, company, model, language, company_info)
    print(f"\nModel: {model}")
    print(
        f"\n{counttokens.num_tokens_from_messages(prompt, model)} prompt tokens counted by num_tokens_from_messages().")
    print(f'{response["usage"]["prompt_tokens"]} prompt tokens counted by the OpenAI API.')
    print(f"\nResult for the company {company}:\n\n{response_content}")
    return response_content


async def main(company, search_terms_google_search, search_terms_google_news, model, language, num_urls_google_search,
               num_urls_google_news, summary_as_txt, summary_as_pdf, report_as_txt, report_as_pdf, company_info):
    get_system_info()
    if not validate_inputs(company, model, language, num_urls_google_search, num_urls_google_news):
        return
    results_google_search, results_google_news = [], []
    tasks_google_search = [limited_execute(execute_google_search, [term], google_search, num_urls_google_search) for
                           term in
                           search_terms_google_search] if search_terms_google_search and num_urls_google_search >= 1 else []
    tasks_google_news = [limited_execute(execute_google_news_rss, [term], google_news_rss, num_urls_google_news) for
                         term in
                         search_terms_google_news] if search_terms_google_news and num_urls_google_news >= 1 else []
    if tasks_google_search or tasks_google_news:
        results_google_search, results_google_news = await asyncio.gather(asyncio.gather(*tasks_google_search),
                                                                          asyncio.gather(*tasks_google_news))
    info_dict_google_search = {key: value for result in results_google_search for key, value in result.items()}
    info_dict_google_news = {key: value for result in results_google_news for key, value in result.items()}
    info_dict_all = {key: info_dict_google_search.get(key, []) + info_dict_google_news.get(key, []) for key in
                     set(info_dict_google_search) | set(info_dict_google_news)}
    for search_term, info_url_list in info_dict_all.items():
        print(f"\nFound URL(s) for the search term '{search_term}': {', '.join(url for info, url in info_url_list)}")
    info_dict_all, full_outputs = await (
        openai_prompt.execute_summarize_each_url(info_dict_all, company, model, language, company_info))
    response_content = generate_report(info_dict_all, company, model, language, company_info)
    output.generate_output(company, full_outputs, summary_as_txt, summary_as_pdf, report_as_txt, report_as_pdf,
                           response_content)


if __name__ == "__main__":
    company_1 = "Apple"
    search_terms_google_search_2 = [company_1]
    search_terms_google_news_3 = [company_1]
    model_4 = "gpt-3.5-turbo-16k"  # "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"
    language_5 = "German"  # "English", "German", "French"
    num_urls_google_search_6 = 3
    num_urls_google_news_7 = 3
    summary_as_txt_8 = True
    summary_as_pdf_9 = True
    report_as_txt_10 = True
    report_as_pdf_11 = True
    company_info_12 = ""
    asyncio.run(main(company_1, search_terms_google_search_2, search_terms_google_news_3, model_4, language_5,
                     num_urls_google_search_6, num_urls_google_news_7, summary_as_txt_8, summary_as_pdf_9,
                     report_as_txt_10, report_as_pdf_11, company_info_12))
