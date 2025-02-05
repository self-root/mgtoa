import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ship_dbaccess import vessel_in_database

def parse_schedule_html(schedule_html) -> list[tuple[str,str]]:
    rows = schedule_html.find("tbody").find_all("tr")
    schedule = list()
    for element in rows:
        expected_arrival = element.find("td").text
        links = element.find("a", class_="named-item", href=True)
        print(links["href"])
        vessel_detail_link = links["href"]
        temp = vessel_detail_link.split("/")
        imo_number = temp[3]
        schedule.append((imo_number, expected_arrival))
    return schedule

def get_ships_arrivals(html_content) ->tuple[str,str]:
    soup = BeautifulSoup(html_content, "html.parser")
    expected = soup.find(id="expected")
    arrivals = soup.find(id="arrivals")
    schedule = parse_schedule_html(expected)
    schedule.extend(parse_schedule_html(arrivals))
    return schedule

def parse_vessel_detail(vessel_detail_html) -> dict[str, str]:
    soup = BeautifulSoup(vessel_detail_html, "html.parser")
    details = soup.find_all("table", class_="tpt1")
    vessel = {}
    first_section = details[0].find_all("td", class_="tpc2")
    second_section = details[2].find_all("td", class_="tpc2")
    keys = ["imo", "name", "type", "flag", "year"]
    vessel.update({k: v for k, v in zip(keys, [v.text for v in first_section])})
    vessel["gross_tonnage"] = second_section[0].text
    param_table = soup.find("table", class_="aparams").find_all("tr")
    for row in param_table:
        if row.find("td", string="Callsign"):
            vessel["callsign"] = row.find("td", class_="v3").text
    flag_icon_div = soup.find("div", class_="title-flag-icon", style=True)["style"]
    url = re.findall(r'\((.*?)\)', flag_icon_div)
    if len(url) > 0:
        vessel["flag_icon"] = url[0]
    return vessel
        


if __name__ == "__main__":
    port_schedule_html = "Port of Toamasina (Madagascar) - Arrivals, Departures, Expected vessels - VesselFinder.html"
    ship_detail = "FENJA BULKER, Bulk Carrier - Details and current position - IMO 1035997 - VesselFinder.html"
    #with open(port_schedule_html, "r") as html:
    #    get_ships_arrivals(html)
    #with open(ship_detail, "r") as detail:
    #    parse_vessel_detail(detail)
    toamasina = "https://www.vesselfinder.com/ports/MGTOA001"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
    port_of_toa_schedule_html = ""
    """with sync_playwright() as pl:
        browser = pl.chromium.launch()
        page = browser.new_page(user_agent=user_agent)
        page.goto(toamasina)
        port_of_toa_schedule_html = page.content()
        browser.close()
    ships = get_ships_arrivals(port_of_toa_schedule_html)"""
    ships = list()
    with open(port_schedule_html, "r") as html:
        ships = get_ships_arrivals(html)
    for imo, _ in ships:
        #Check if vessel details already exist in database
        #if not, 
        if not vessel_in_database(imo):
            vessel_detail_url = f"https://www.vesselfinder.com/vessels/details/{imo}"
            with sync_playwright() as pl:
                browser = pl.chromium.launch()
                page = browser.new_page(user_agent=user_agent)
                page.goto(vessel_detail_url)
                vessel_detail_html = page.content()
                vessel_detail = parse_vessel_detail(vessel_detail_html)
        
    



# pip install mysql-connector-python