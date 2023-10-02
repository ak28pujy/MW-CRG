import asyncio

import openai
from aiohttp import ClientSession


async def execute_summarize_each_url(info_dict, company, model, language, company_info):
    summarized_info = {}
    full_outputs = ""
    async with ClientSession() as session:
        openai.aiosession.set(session)
        tasks = []
        for search_term, info_url_list in info_dict.items():
            summarized_info[search_term] = []
            for info, url in info_url_list:
                task = summarize_each_url(info, url, company, model, language, company_info)
                tasks.append((task, search_term))
        try:
            results = await asyncio.gather(*[t for t, _ in tasks], return_exceptions=True)
            for (summary, url, full_output), search_term in zip(results, [st for _, st in tasks]):
                if isinstance(summary, Exception):
                    print(f"\nAn error has occurred at search term: {search_term} - {str(summary)}")
                else:
                    summarized_info[search_term].append((summary, url))
                    full_outputs += full_output + "\n"
        except Exception as e:
            print(f"\nAn unexpected error has occurred: {str(e)}")
    await openai.aiosession.get().close()
    return summarized_info, full_outputs


async def summarize_each_url(info, url, company, model, language, company_info):
    try:
        prompt = [{"role": "user", "content": f"Please analyze the following web page ({url}) and create a brief "
                                              f"summary of relevant information about the company {company}. "},
                  {"role": "user", "content": f"Website content:\n\n\n{info}\n\n\n"},
                  {"role": "user", "content": "Focus on clear, concrete, and useful details when extracting "
                                              f"information. Please reply in {language}. "}]
        if company_info:
            company_info_prompt = {"role": "user", "content": "Pay particular attention to the following information: "
                                                              f"{company_info}. "}
            prompt.insert(1, company_info_prompt)
        response = await openai.ChatCompletion.acreate(model=model, messages=prompt, temperature=1.0, top_p=1.0, n=1,
                                                       frequency_penalty=0.0, presence_penalty=0.0)
        full_output = f"\n{url} :\n\n{response['choices'][0]['message']['content']}"
        summary = response['choices'][0]['message']['content']
        print(full_output)
        return summary, url, full_output
    except Exception as e:
        print(f"\nAn error has occurred at URL: {url} - {str(e)}")
        return str(e), url, f"Error: {str(e)}"


def summarize(info_dict, company, model, language, company_info):
    try:
        prompt = [{"role": "user", "content": "Please create a structured overview for an IT consulting firm's client "
                                              f"acquisition efforts to attract {company} as a new client. "
                                              "Consider the following aspects:\n\n"
                                              "1. **General Company Information:**\n"
                                              "   - Company name\n"
                                              "   - Date of incorporation\n"
                                              "   - Founder\n"
                                              "   - Current CEO\n"
                                              "   - Headquarters\n"
                                              "   - Industry\n"
                                              "   - Company website\n\n"
                                              "2. **Product and service portfolio:**\n"
                                              "   - Main products and services\n"
                                              "   - Unique selling proposition (USP)\n"
                                              "   - Statements from industry experts, journalists or "
                                              "other relevant third parties\n\n"
                                              "3. **Organization and staff:**\n"
                                              "   - Number of employees\n"
                                              "   - Organizational structure\n\n"
                                              "4. **Financial and market information:**\n"
                                              "   - Business figures\n"
                                              "   - Market position\n\n"
                                              "5. **Corporate strategy, vision and reputation:**\n"
                                              "   - Corporate mission and vision\n"
                                              "   - Business highlights\n"
                                              "   - Future projects\n"
                                              "   - Social responsibility\n"
                                              "   - Awards and recognitions\n\n"}]
        for search_term, info_url_list in info_dict.items():
            for info, url in info_url_list:
                prompt.append({"role": "user", "content": "Here is additional information I found on a website "
                                                          f"({url}):\n\n\n{info}\n\n\n"})
        prompt.append({"role": "user", "content": "Please integrate only the relevant information and concrete figures "
                                                  f"regarding the above aspects in the profile about {company}. "
                                                  "Use your general knowledge to complete. If there is no knowledge or "
                                                  "information on any of the above aspects, remove the relevant field. "
                                                  "Finally, summarize the above-mentioned aspects in a "
                                                  f"continuous text. Please reply in {language}. "})
        if company_info:
            company_info_prompt = {"role": "user", "content": "Pay particular attention to the following information: "
                                                              f"{company_info}. "}
            prompt.insert(2, company_info_prompt)
        response = openai.ChatCompletion.create(model=model, messages=prompt, temperature=1.0, top_p=1.0, n=1,
                                                frequency_penalty=0.0, presence_penalty=0.0)
        return response['choices'][0]['message']['content'], prompt, response
    except Exception as e:
        print(f"\nAn error occurred when summarizing the information for {company}: {str(e)}")
        return str(e), None, None
