import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ship_dbaccess import *
from logger_conf import get_logger
import time

logger = get_logger(__name__)

def parse_schedule_html(schedule_html, s_type: str) -> list[tuple[str,str,str]]:
    """
    s_type is either expected or arrival
    """
    rows = schedule_html.find("tbody").find_all("tr")
    schedule = list()
    for element in rows:
        expected_arrival = element.find("td").text
        links = element.find("a", class_="named-item", href=True)
        print(links["href"])
        vessel_detail_link = links["href"]
        temp = vessel_detail_link.split("/")
        imo_number = temp[3]
        schedule.append((imo_number, expected_arrival, s_type))
    return schedule

def get_ships_arrivals(html_content) ->list[tuple[str,str,str]]:
    soup = BeautifulSoup(html_content, "html.parser")
    expected = soup.find(id="expected")
    arrivals = soup.find(id="arrivals")
    schedule = parse_schedule_html(expected, "expected")
    schedule.extend(parse_schedule_html(arrivals, "arrival"))
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
    toamasina = "https://www.vesselfinder.com/ports/MGTOA001"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
    port_of_toa_schedule_html = ""
    with sync_playwright() as pl:
        browser = pl.chromium.launch()
        page = browser.new_page(user_agent=user_agent)
        logger.debug(f"Fetching {toamasina=}")
        page.goto(toamasina)
        port_of_toa_schedule_html = page.content()
        browser.close()
        logger.debug(f"Fetched {toamasina=}")
    schedules = get_ships_arrivals(port_of_toa_schedule_html)

    for schedule in schedules:
        if len(schedule[0]) == 9: # No IMO number, only MMIS
            continue
        if not vessel_in_database(schedule[0]):
            vessel_detail_url = f"https://www.vesselfinder.com/vessels/details/{schedule[0]}"
            with sync_playwright() as pl:
                browser = pl.chromium.launch()
                page = browser.new_page(user_agent=user_agent)
                logger.debug(f"Fetching {vessel_detail_url=}")
                page.goto(vessel_detail_url)
                vessel_detail_html = page.content()
                vessel_detail = parse_vessel_detail(vessel_detail_html)
                add_vessel(vessel_detail)
                logger.debug(f"Added vessel {schedule[0]=} to the database")
                browser.close()
            time.sleep(3)
        ship = get_vessel(schedule[0])
        if not ship_schedule_exists(schedule, ship.get_id()):
            logger.debug(f"Adding {schedule=} into the database")
            add_ship_schedule(schedule, ship.get_id())
        
    



# pip install mysql-connector-python