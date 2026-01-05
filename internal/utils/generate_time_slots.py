from datetime import datetime, timedelta, time
from dataclasses import dataclass
from internal.constants import constants

@dataclass
class TimeSlot:
    StartTime: datetime
    EndTime: datetime
    Label: str

def generate_time_slots() -> list[TimeSlot]:
    slots = []

    base_date = datetime.today().date()

    current = datetime.combine(base_date, time(constants.START_TIME_OF_SERVICE, 0))
    end_of_service = datetime.combine(base_date, time(constants.END_TIME_OF_SERVICE, 0))
    
    slot_duration = timedelta(minutes=constants.TIME_LIMIT_OF_SLOT)

    while current + slot_duration <= end_of_service:
        next_slot_end = current + slot_duration
        
        slots.append(TimeSlot(
            current,
            next_slot_end,
            f"{current.strftime(constants.TIME_LAYOUT)} - {next_slot_end.strftime(constants.TIME_LAYOUT)}"
        ))
        
        current = next_slot_end

    return slots


def is_slot_in_past(slot_label: str, target_date_str: str) -> bool:
    start_time_str = slot_label.split(" - ")[0].strip()

    slot_datetime = datetime.strptime(f"{target_date_str} {start_time_str}", "%d-%m-%Y %I:%M %p")
    
    return slot_datetime < datetime.now()