import asyncio
import os
import platform
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import feedparser
import openai
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService

import counttokens
import pdf

OPENAI_API_KEY = 'OPENAI_API_KEY'
GOOGLE_API_KEY = 'GOOGLE_API_KEY'
GOOGLE_CSE_ID = 'GOOGLE_CSE_ID'
MAX_CONCURRENT_TASKS = 'MAX_CONCURRENT_TASKS'
MAX_CONCURRENT_URLS = 'MAX_CONCURRENT_URLS'
PAGE_LOAD_TIMEOUT = 'PAGE_LOAD_TIMEOUT'

OUTPUT_PATH = './output/'
DRIVERS_PATH = './driver/'

load_dotenv()
openai.api_key = os.getenv(OPENAI_API_KEY)
google_api_key = os.getenv(GOOGLE_API_KEY)
google_cse_id = os.getenv(GOOGLE_CSE_ID)
semaphore = asyncio.Semaphore(int(os.getenv(MAX_CONCURRENT_TASKS, 3)))
max_concurrent_urls = int(os.getenv(MAX_CONCURRENT_URLS, 5))
page_load_timeout = int(os.getenv(PAGE_LOAD_TIMEOUT, 15))


async def limited_execute(task, *args):
    async with semaphore:
        return await task(*args)


def get_system_info():
    print('OS:', platform.system())
    print('Architecture:', platform.machine())


def get_driver_path(driver_name):
    os_name = platform.system()
    arch = 'intel' if 'x86_64' in platform.machine() or 'AMD64' in platform.machine() else 'arm'
    os_name = 'windows' if os_name == 'Windows' else 'mac' if os_name == 'Darwin' else 'linux'
    if (os_name == 'windows' or os_name == 'linux') and arch == 'arm':
        raise ValueError(f"{os_name.capitalize()} ARM is not supported")
    exe_extension = '.exe' if os_name == 'windows' else ''
    return f"{DRIVERS_PATH}{os_name}/{arch}/{driver_name}{exe_extension}"


BROWSERS = [{"driver": webdriver.Firefox, "path": get_driver_path("geckodriver"), "service": FirefoxService},
            {"driver": webdriver.Chrome, "path": get_driver_path("chromedriver"), "service": ChromeService}]


def get_browser(browser):
    try:
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
            return browser["driver"](options=chrome_options,
                                     service=browser["service"](executable_path=browser["path"]))
    except Exception as e:
        print(f"Error with {browser['driver'].__name__}: {e}")
        return None


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
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(search_term)}&hl=de&gl=DE&ceid=DE:de"
    feed = feedparser.parse(url)
    return [(entry.title, entry.link) for entry in feed.entries[:num]]


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
        browser = get_browser(browser)
        page_content = get_page_content(browser, url)
        if page_content:
            return page_content
    return ""


def get_page_content(browser, url):
    page_text = ""
    if not browser:
        print("\nError: Browser instance is None")
        return ""
    try:
        browser.set_page_load_timeout(page_load_timeout)
        browser.get(url)
        if '.google.com' in url:
            try:
                browser.find_element(By.XPATH, "//.[@aria-label='Alle akzeptieren']").click()
                time.sleep(5)
            except Exception as e:
                print(f"\nError clicking the accept button on Google: {e}")
        page_text = BeautifulSoup(browser.page_source, 'html.parser').get_text()
    except Exception as e:
        print(f"\nError fetching the URL {url}: {e}")
    finally:
        browser.quit()
    return page_text


async def execute_summarize_each_url(info_dict, company, model, language):
    summarized_info = {}
    async with ClientSession() as session:
        openai.aiosession.set(session)
        tasks = []
        for search_term, info_url_list in info_dict.items():
            summarized_info[search_term] = []
            for info, url in info_url_list:
                task = summarize_each_url(info, url, company, model, language)
                tasks.append((task, search_term))
        results = await asyncio.gather(*[t for t, _ in tasks])
        for result, search_term in zip(results, [st for _, st in tasks]):
            summarized_info[search_term].append(result)
    await openai.aiosession.get().close()
    return summarized_info


async def summarize_each_url(info, url, company, model, language):
    prompt = [{"role": "user",
               "content": f"Bitte analysiere die folgende Webseite ({url}), auf der {company} erwähnt wird, und "
                          "erstelle eine prägnante Zusammenfassung der relevanten Informationen."},
              {"role": "user", "content": f"Inhalt der Webseite:\n\n{info}"},
              {"role": "user", "content": "Fokussiere dich beim Extrahieren der Informationen auf klare, konkrete und "
                                          "nützliche Details, und vermeide dabei irrelevante oder redundante Inhalte. "
                                          f"Die Antwort sollte in {language} verfasst sein."}]
    response = await openai.ChatCompletion.acreate(model=model, messages=prompt, temperature=1, top_p=1.0, n=1,
                                                   frequency_penalty=0.0, presence_penalty=0.0)
    print(f"\n{url}:\n", response['choices'][0]['message']['content'])
    summary = response['choices'][0]['message']['content']
    return summary, url


def summarize(info_dict, company, model, language):
    prompt = [{"role": "system",
               "content": "Du bist ein kenntnisreicher KI-Assistent, spezialisiert auf Unternehmensanalysen."},
              {"role": "user", "content": "Bitte erstelle eine strukturierte Übersicht für die Kundenakquise eines "
                                          f"IT-Beratungsunternehmens, um {company} als Neukunden zu gewinnen. "
                                          "Berücksichtige dabei die folgenden Aspekte und fasse im Anschluss "
                                          "die Informationen in einem Fließtext zusammen:\n\n"
                                          "1. **Allgemeine Unternehmensinformationen:**\n"
                                          "   - Unternehmensname\n"
                                          "   - Gründungsdatum\n"
                                          "   - Gründer\n"
                                          "   - Aktueller CEO\n"
                                          "   - Hauptsitz\n"
                                          "   - Branche\n"
                                          "   - Website des Unternehmens\n\n"
                                          "2. **Produkt- und Dienstleistungsportfolio:**\n"
                                          "   - Hauptprodukte und -dienstleistungen\n"
                                          "   - USP oder Alleinstellungsmerkmale\n"
                                          "   - Aussagen von Branchenexperten, Journalisten oder "
                                          "anderen relevante Dritten\n\n"
                                          "3. **Organisation und Mitarbeiter:**\n"
                                          "   - Anzahl der Mitarbeiter\n"
                                          "   - Organisationsstruktur\n\n"
                                          "4. **Finanzielle und Marktinformationen:**\n"
                                          "   - Geschäftszahlen\n"
                                          "   - Marktposition\n\n"
                                          "5. **Unternehmensstrategie, -vision und -reputation:**\n"
                                          "   - Unternehmensmission und -vision\n"
                                          "   - Geschäftliche Höhepunkte\n"
                                          "   - Zukunftsprojekte\n"
                                          "   - Soziale Verantwortung\n"
                                          "   - Auszeichnungen und Anerkennungen\n\n"}]
    for search_term, info_url_list in info_dict.items():
        for info, url in info_url_list:
            prompt.append(
                {"role": "user", "content": f"Hier sind zusätzliche Informationen, die ich auf einer Webseite ({url}) "
                                            f"gefunden habe, welche {company} erwähnt. Diese wurden bereits von "
                                            f"der OpenAI API in einer anderen Anfrage verarbeitet: {info}"})
    prompt.append({"role": "user", "content": "Integriere bitte nur die relevanten Informationen bezüglich der "
                                              f"oben genannten Aspekte in den Steckbrief von {company}. Sollten einige "
                                              "Informationen fehlen, nutze dein allgemeines Wissen, wenn es sinnvoll "
                                              "und zutreffend ist, ansonsten lass das betreffende Feld leer. "
                                              f"Gehe dabei systematisch vor und antworte bitte in {language}."})
    response = openai.ChatCompletion.create(model=model, messages=prompt, temperature=1, top_p=1.0, n=1,
                                            frequency_penalty=0.0, presence_penalty=0.0)
    return response['choices'][0]['message']['content'], prompt, response


def generate_report(info_dict, company, model, language, prompt_as_txt, report_as_txt, report_as_pdf):
    response_content, prompt, response = summarize(info_dict, company, model, language)
    print(f"\nModel: {model}")
    print(
        f"\n{counttokens.num_tokens_from_messages(prompt, model)} prompt tokens counted by num_tokens_from_messages().")
    print(f'{response["usage"]["prompt_tokens"]} prompt tokens counted by the OpenAI API.')
    print(f"\nResult for the company {company}:\n\n{response_content}")
    if prompt_as_txt:
        write_content_to_file(company, prompt, 'Prompt')
    if report_as_txt:
        write_content_to_file(company, response_content, 'Bericht')
    if report_as_pdf:
        write_report_to_pdf(company, response_content, report_as_txt)
    return response_content


def write_content_to_file(company, content, file_type):
    file_path = get_file_path(file_type, company)
    with open(f'{file_path}.txt', "w", encoding='utf-8') as file:
        file.write(str(content))


def write_report_to_pdf(company, content, report_as_txt):
    file_path = get_file_path('Bericht', company)
    with open(f'{file_path}.txt', "w", encoding='utf-8') as file:
        file.write(content)
    pdf.text_to_pdf(f'{file_path}.txt', f'{file_path}.pdf')
    if not report_as_txt:
        os.remove(f'{file_path}.txt')


def get_file_path(file_type, company):
    return f'{OUTPUT_PATH}{date.today()} - {company} - {file_type}'


async def main(company, search_terms_google_search, search_terms_google_news, model, language, num_urls_google_search,
               num_urls_google_news, prompt_as_txt, report_as_txt, report_as_pdf):
    get_system_info()
    if not (company and model and language):
        print(f"\nInvalid input. Please check the parameters.")
        return
    if num_urls_google_search > 10:
        print(f"\nInvalid input. Number of URLs from Google Search must not be higher than 10.")
        return
    if num_urls_google_news > 15:
        print(f"\nInvalid input. Number of URLs from Google News must not be higher than 15.")
        return
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    results_google_search = []
    results_google_news = []

    if search_terms_google_search and num_urls_google_search >= 1:
        tasks_google_search = [limited_execute(execute_google_search, [term], google_search, num_urls_google_search) for
                               term in search_terms_google_search]
        results_google_search = await asyncio.gather(*tasks_google_search)
    if search_terms_google_news and num_urls_google_news >= 1:
        tasks_google_news = [limited_execute(execute_google_news_rss, [term], google_news_rss, num_urls_google_news) for
                             term in search_terms_google_news]
        results_google_news = await asyncio.gather(*tasks_google_news)

    info_dict_google_search = {key: value for result in results_google_search for key, value in result.items()}
    info_dict_google_news = {key: value for result in results_google_news for key, value in result.items()}

    info_dict_all = {key: info_dict_google_search.get(key, []) + info_dict_google_news.get(key, []) for key in
                     set(info_dict_google_search) | set(info_dict_google_news)}

    for search_term, info_url_list in info_dict_all.items():
        print(f"\nFound URL(s) for the search term '{search_term}': {', '.join(url for info, url in info_url_list)}")

    info_dict_all = await execute_summarize_each_url(info_dict_all, company, model, language)

    generate_report(info_dict_all, company, model, language, prompt_as_txt, report_as_txt, report_as_pdf)


if __name__ == "__main__":
    company_1 = "NOW GMBH"
    search_terms_google_search_2 = [company_1]
    search_terms_google_news_3 = [company_1]
    model_4 = "gpt-3.5-turbo-16k"  # "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"
    language_5 = "German"  # "English", "German", "French"
    num_urls_google_search_6 = 10
    num_urls_google_news_7 = 10
    prompt_as_txt_8 = True
    report_as_txt_9 = True
    report_as_pdf_10 = True
    asyncio.run(main(company_1, search_terms_google_search_2, search_terms_google_news_3, model_4, language_5,
                     num_urls_google_search_6, num_urls_google_news_7, prompt_as_txt_8, report_as_txt_9,
                     report_as_pdf_10))
