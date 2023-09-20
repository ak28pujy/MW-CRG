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
                    print(f"An error has occurred at URL: {search_term} - {str(summary)}")
                else:
                    summarized_info[search_term].append((summary, url))
                    full_outputs += full_output + "\n"
        except Exception as e:
            print(f"An unexpected error has occurred: {str(e)}")

    await openai.aiosession.get().close()
    return summarized_info, full_outputs


async def summarize_each_url(info, url, company, model, language, company_info):
    try:
        prompt = [{"role": "user",
                   "content": f"Bitte analysiere die folgende Webseite ({url}), auf der {company} erwähnt wird, "
                              "und erstelle eine prägnante Zusammenfassung der relevanten Informationen."},
                  {"role": "user", "content": f"Inhalt der Webseite:\n\n\n{info}\n\n\n"},
                  {"role": "user", "content": "Fokussiere dich beim Extrahieren der Informationen auf klare, "
                                              "konkrete und nützliche Details, und vermeide dabei irrelevante "
                                              "oder redundante Inhalte. "
                                              f"Die Antwort sollte in {language} verfasst sein."}]
        if company_info:
            company_info_prompt = {"role": "user", "content": f"Achte insbesondere auf folgende Informationen über "
                                                              f"{company}: {company_info}."}
            prompt.insert(1, company_info_prompt)
        response = await openai.ChatCompletion.acreate(model=model, messages=prompt, temperature=1, top_p=1.0, n=1,
                                                       frequency_penalty=0.0, presence_penalty=0.0)
        full_output = f"\n{url}:\n\n{response['choices'][0]['message']['content']}"
        summary = response['choices'][0]['message']['content']
        print(full_output)
        print(prompt)
        return summary, url, full_output
    except Exception as e:
        print(f"An error has occurred at URL: {url} - {str(e)}")
        return e


def summarize(info_dict, company, model, language, company_info):
    try:
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
                    {"role": "user", "content": "Hier sind zusätzliche Informationen, die ich auf einer Webseite "
                                                f"({url}) gefunden habe, welche {company} erwähnt. "
                                                "Diese wurden bereits von der OpenAI API in einer anderen Anfrage "
                                                f"verarbeitet:\n\n\n{info}\n\n\n"})
        prompt.append({"role": "user", "content": "Integriere bitte nur die relevanten Informationen bezüglich der "
                                                  f"oben genannten Aspekte in den Steckbrief von {company}. "
                                                  "Sollten einige Informationen fehlen, nutze dein allgemeines Wissen, "
                                                  "wenn es sinnvoll und zutreffend ist, ansonsten lass das "
                                                  "betreffende Feld leer. Gehe dabei systematisch vor und "
                                                  f"antworte bitte in {language}."})
        if company_info:
            company_info_prompt = {"role": "user", "content": f"Achte insbesondere auf folgende Informationen über "
                                                              f"{company}: {company_info}."}
            prompt.insert(2, company_info_prompt)
        response = openai.ChatCompletion.create(model=model, messages=prompt, temperature=1, top_p=1.0, n=1,
                                                frequency_penalty=0.0, presence_penalty=0.0)
        return response['choices'][0]['message']['content'], prompt, response
    except Exception as e:
        print(f"An error occurred when summarizing the information for {company}: {str(e)}")
        return str(e), None, None
