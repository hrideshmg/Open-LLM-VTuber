import requests
from bs4 import BeautifulSoup
import json
import sys


def scrape_olabs_experiment(experiment_url):
    base_url = "https://www.olabs.edu.in/"

    try:
        r = requests.get(experiment_url)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch experiment page: {str(e)}"}

    result = {
        "Aim": "",
        "Theory": "",
        "Outcomes": [],
        "Materials required": [],
        "Simulator Procedure": [],
    }

    for h1 in soup.find_all("h1"):
        if any(
            word in h1.get_text().lower()
            for word in ["aim:", "objective:", "aim", "objective"]
        ):
            next_element = h1.find_next()
            if next_element:
                result["Aim"] = next_element.get_text().strip()
            break

    theory_content = []
    theory_ended = False

    theory_heading = None
    for h1 in soup.find_all("h1"):
        if any(word in h1.get_text().lower() for word in ["theory:", "theory"]):
            theory_heading = h1
            break

    if theory_heading:
        current = theory_heading.find_next()
        while current and not theory_ended:
            if current.name == "h1":
                theory_ended = True
                continue

            if current.name in ["p", "div", "span", "ul", "ol", "table"]:
                if current.name in ["ul", "ol"]:
                    list_text = "\n".join(
                        f"• {li.get_text().strip()}" for li in current.find_all("li")
                    )
                    theory_content.append(list_text)
                else:
                    text = current.get_text().strip()
                    if text:
                        theory_content.append(text)

            current = current.find_next()

    result["Theory"] = "\n\n".join(theory_content)

    for h1 in soup.find_all("h1"):
        if any(word in h1.get_text().lower() for word in ["outcomes", "outcomes:"]):
            outcomes_list = h1.find_next().find_all("li")
            result["Outcomes"] = [li.get_text().strip() for li in outcomes_list]
            break

    procedure_url = None

    tab_element = soup.find("ul", id="tab")
    if tab_element and tab_element.find_all("a") and len(tab_element.find_all("a")) > 1:
        procedure_url = base_url + tab_element.find_all("a")[1]["href"]

    if not procedure_url:
        for link in soup.find_all("a"):
            if "procedure" in link.get_text().lower() and "href" in link.attrs:
                procedure_url = (
                    base_url + link["href"]
                    if not link["href"].startswith("http")
                    else link["href"]
                )
                break

    if not procedure_url:
        import re

        match = re.search(r"sim=(\d+)", experiment_url)
        if match:
            sim_id = match.group(1)
            procedure_url = f"{base_url}?sub=1&brch=6&sim={sim_id}&cnt=4"

    if not procedure_url:
        result["error"] = "Could not determine procedure URL"
        return result

    try:
        r = requests.get(procedure_url)
        r.raise_for_status()
        procedure_soup = BeautifulSoup(r.content, "html.parser")
    except requests.exceptions.RequestException as e:
        result["error"] = f"Failed to fetch procedure page: {str(e)}"
        return result
    for heading in procedure_soup.find_all(["h1", "h2", "h3", "h4"]):
        if "material" in heading.get_text().lower():
            next_tag = heading.find_next()
            while next_tag and next_tag.name not in ["h1", "h2", "h3", "h4"]:
                if next_tag.name == "ul":
                    result["Materials required"] = [
                        li.get_text().strip() for li in next_tag.find_all("li")
                    ]
                    break
                next_tag = next_tag.find_next()

    for heading in procedure_soup.find_all(["h1", "h2", "h3", "h4"]):
        if "procedure" in heading.get_text().lower():
            next_tag = heading.find_next()
            while next_tag and next_tag.name not in ["h1", "h2", "h3", "h4"]:
                if next_tag.name == "ul" or next_tag.name == "ol":
                    result["Simulator Procedure"] = [
                        li.get_text().strip() for li in next_tag.find_all("li")
                    ]
                    break
                next_tag = next_tag.find_next()
    if not result["Simulator Procedure"]:
        lists = procedure_soup.find_all(["ul", "ol"])
        if lists and len(lists) > 2:
            result["Simulator Procedure"] = [
                li.get_text().strip() for li in lists[2].find_all("li")
            ]

    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        result = scrape_olabs_experiment(url)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"error": "No URL provided"}, indent=2))
