from ship_models import *
from logger_conf import get_logger
from datetime import datetime


logger = get_logger(__name__)

def vessel_in_database(imo: str) -> bool:
    try:
        with database:
            return ToaShip.get_or_none(ToaShip.imo == imo) is not None
    except:
        logger.exception(f"param: {imo=}\n")
    
def get_vessel(imo: str) -> ToaShip | None:
    try:
        with database:
            vessel = ToaShip.get_or_none(ToaShip.imo == imo)
            return vessel
    except:
        logger.exception(f"param: {imo=}\n")

def add_vessel(vessel: dict[str, any]):
    try:
        with database:
            ship = ToaShip(
                call_sign = vessel["callsign"],
                flag = vessel["flag"],
                flag_url = vessel["flag_icon"],
                gross_tonnage = vessel["gross_tonnage"],
                imo = vessel["imo"],
                ship_type = vessel["type"],
                year = vessel["year"]
            )
            ship.save()
    except:
        logger.exception(f"param: {vessel=}\n")

def ship_schedule_exists(shchedule: tuple[str, str, str], ship_id) -> bool:
    try:
        with database:
            db_schedule = ToaSchedule.get_or_none(
                ToaSchedule.schedule_date==schedule_date_to_datetime(shchedule[1]).isoformat(),
                ToaSchedule.ship==ship_id,
                ToaSchedule.schedule_type==shchedule[2]
            )
            return db_schedule is not None
    except:
        logger.exception(f"param: {shchedule=}\n")

def add_ship_schedule(schedule: tuple[str, str, str], id):
    s_date = schedule_date_to_datetime(schedule[1])
    
    try:
        with database:
            toa_schedule = ToaSchedule(
            schedule_date = s_date.isoformat(),
            ship = id,
            schedule_type = schedule[2]
        )
            toa_schedule.save()
    except:
        logger.exception(f"Schedule: {schedule=}")

def schedule_date_to_datetime(str_date) -> datetime:
    s_date = datetime.strptime(str_date, "%b %d, %H:%M")
    s_date = s_date.replace(year=datetime.now().year)
    return s_date

if __name__ == "__main__":
    sched = ("9715206", "Feb 8, 07:00", "expected")
    if ship_schedule_exists(sched, 1):
        print("It exists")
    else:
        print("Does not")