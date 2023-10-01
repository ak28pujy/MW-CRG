import asyncio

import openai
from aiohttp import ClientSession


# Let's work this out in a step by step way to be sure we have the right answer.


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
        prompt = [
            {"role": "user", "content": f"Bitte analysiere die folgende Webseite ({url}) und erstelle eine prägnante "
                                        "Zusammenfassung der relevanten Informationen über das Unternehmen "
                                        f"{company}. "},
            {"role": "user", "content": f"Inhalt der Webseite:\n\n\n{info}\n\n\n"},
            {"role": "user", "content": "Fokussiere dich beim Extrahieren der Informationen auf klare, "
                                        f"konkrete und nützliche Details. Die Antwort soll in {language} verfasst "
                                        "sein. Gehe dabei systematisch vor."}]
        if company_info:
            company_info_prompt = {"role": "user", "content": "Achte insbesondere auf folgende Informationen: "
                                                              f"{company_info}. "}
            prompt.insert(1, company_info_prompt)
        response = await openai.ChatCompletion.acreate(model=model, messages=prompt, temperature=1, top_p=1.0, n=1,
                                                       frequency_penalty=0.0, presence_penalty=0.0)
        full_output = f"\n{url}:\n\n{response['choices'][0]['message']['content']}"
        summary = response['choices'][0]['message']['content']
        print(full_output)
        return summary, url, full_output
    except Exception as e:
        print(f"\nAn error has occurred at URL: {url} - {str(e)}")
        return str(e), url, f"Error: {str(e)}"


def summarize(info_dict, company, model, language, company_info):
    try:
        prompt = [{"role": "system", "content": "Du bist ein hilfreicher Assistent. "},
                  {"role": "user", "content": "Bitte erstelle eine strukturierte Übersicht für die Kundenakquise eines "
                                              f"IT-Beratungsunternehmens, um {company} als Neukunden zu gewinnen. "
                                              "Berücksichtige dabei die folgenden Aspekte:\n\n"
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
                    {"role": "user", "content": "Hier sind zusätzliche Informationen, die ich auf einer Webseite "
                                                f"({url}) gefunden habe:\n\n\n{info}\n\n\n"})
        prompt.append({"role": "user", "content": "Integriere bitte nur die relevanten Informationen und "
                                                  "konkrete Zahlen bezüglich der oben genannten Aspekte in den "
                                                  f"Steckbrief über {company}. Nutze zur Ergänzung dein "
                                                  "allgemeines Wissen. Wenn kein Wissen oder Informationen zu einem "
                                                  "der oben genannten Aspekte vorhanden sind, entferne das betreffende "
                                                  "Feld. Fasse abschließend die oben genannten Aspekte zusätzlich "
                                                  f"in einem Fließtext zusammen. Die Antwort soll in {language} "
                                                  "verfasst sein. Gehe dabei systematisch vor."})
        if company_info:
            company_info_prompt = {"role": "user", "content": "Achte insbesondere auf folgende Informationen: "
                                                              f"{company_info}. "}
            prompt.insert(2, company_info_prompt)
        response = openai.ChatCompletion.create(model=model, messages=prompt, temperature=1, top_p=1.0, n=1,
                                                frequency_penalty=0.0, presence_penalty=0.0)
        return response['choices'][0]['message']['content'], prompt, response
    except Exception as e:
        print(f"\nAn error occurred when summarizing the information for {company}: {str(e)}")
        return str(e), None, None
