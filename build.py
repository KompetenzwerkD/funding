import yaml
import urllib
import datetime
import json
from smw_utils.api import MediawikiApi


def get_property(page, property_label):
    for prop in page["properties"]:
        if prop["property"]["label"] == property_label:
            if "label" in prop:
                return prop["label"]
            else:
                return prop["value"]
    return ""


def create_funding_page_file(page_data):
    deadline = get_property(page_data, "Has deadline")
    title = page_data["title"]

    filename = title.replace(" ","_").replace("/", "_").replace(".","").replace(":","").replace("?", "")
    filename = filename.lower()
    filepath = f"ausschreibungen/{filename}.md"    

    #for page_data in pages:
    f_content = "[zurück](/funding/)"
    f_content += f"\n\n## {title}\n\n"
    deadline = get_property(page_data, "Has deadline")
    institution = get_property(page_data, "Has funding institution")
    homepage = get_property(page_data, "Has homepage")

    f_content += f"* Nächste Einreichung: {deadline}"
    f_content += f"\n* Institution: {institution}"

    free_text = page_data["free_text"]
    f_content += f"\n\n{free_text}"

    if homepage:
        f_content += f"\n\n* [Link]({homepage})"
    
    with open(filepath, "w") as f:
        f.write(f_content)


def get_funding_pages():
    with open("config.yml") as f:
        config = yaml.load(f, Loader=yaml.BaseLoader)

    api = MediawikiApi(
        config["url"],
        config["api"],
        config["lgname"],
        config["lgpassword"],
        verbose=True
    )

    page_titles = api.fetch_category("Funding")
    

    pages = []
    for page_title in page_titles:
        page_data = api.fetch_page(page_title)
        pages.append(page_data)

    content = "# Ausschreibungen"
    content += f"\n\n* Stand: {datetime.datetime.now().isoformat()[:10]}"
    content += "\n\n Kuratierte Liste von Ausschreibungen und Fördermöglichkeiten für geistes- und sozialwissenschaftliche Forschung mit Schwerpunkt auf Digital Humanities. Die Kuratierung erfolgt durch das [KompetenzwerkD](https://kompetenzwerkd.saw-leipzig.de) an der [Sächsischen Akademie der wissenschaften zu Leipzig](https://www.saw-leipzig.de). Das vollständige Datenset ist auch als [.json Datei downloadbar](dataset/ausschreibungen.json)."

    pages = sorted(pages, key=lambda x: get_property(x, "Has deadline"))

    today = datetime.datetime.now().isoformat()[:10]
    upcoming = []
    past = []

    for page in pages:
        page_date = get_property(page, "Has deadline")
        if page_date < today:
            past.append(page)
        else:
            upcoming.append(page)


    content += f"\n\n## Aktuelle Ausschreibungen\n"
    for page_data in upcoming:
        deadline = get_property(page_data, "Has deadline")
        title = page_data["title"]
        filename = title.replace(" ","_").replace("/", "_").replace(".","").replace(":","").replace("?", "")
        filename = filename.lower()
        filepath = f"ausschreibungen/{filename}.md"
        content += f"\n* [{deadline} - {title}]({filepath})"

        create_funding_page_file(page_data)

    content += f"\n\n## Vergangenge Ausschreibungen\n"
    for page_data in past:
        deadline = get_property(page_data, "Has deadline")
        title = page_data["title"]
        filename = title.replace(" ","_").replace("/", "_").replace(".","").replace(":","").replace("?", "")
        filename = filename.lower()
        filepath = f"ausschreibungen/{filename}.md"
        content += f"\n* [{deadline} - {title}]({filepath})"

        create_funding_page_file(page_data)


    with open("index.md", "w") as f:
        f.write(content)
    
    with open("dataset/ausschreibungen.json", "w") as f:
        json.dump(pages, f, indent=4)

if __name__ == "__main__":
    get_funding_pages()