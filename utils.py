from datetime import datetime ,time
from  services.dbconnection import DbService
from datetimerange import DateTimeRange
import datetime as dt
from errno import ETIME

DURATION = 30
dbservice = DbService()
company_id = 3
company_promotion= dbservice.list_valid_promotions(company_id)
ALL_PROMOTIONS = []
for promotion in company_promotion:
    ALL_PROMOTIONS.append(promotion['title'])

company_services = dbservice.list_main_services(company_id)
ALL_SERVICES = []
for service in company_services:
    ALL_SERVICES.append(service['info']['title'])


ALL_APPOINTMENTS = ['appointment 1','appointment 2','appointment 3','appointment 4','appointment 5','appointment 6']
AMPM = ['am','pm']

def appointment_date_formator(appointment_date):
    appointment_date=appointment_date.replace(' ', '')
    try:
        if '/' in appointment_date:
            appointment_date = datetime.strptime(appointment_date, "%d/%m/%Y")
        elif '-' in appointment_date:
            appointment_date = datetime.strptime(appointment_date, "%d-%m-%Y")
    except:
        return False
    days_between = (appointment_date-datetime.today()).days
    if days_between>7 or days_between<0:
        return False
    else:
        return appointment_date

def appointment_time_validator(appointment_time):
    appointment_time = appointment_time.replace(' ', '')
    try:
        if any(x in appointment_time.lower() for x in AMPM):
            appointment_time = datetime.strptime(appointment_time, "%I:%M%p")
        else:
            appointment_time = datetime.strptime(appointment_time, "%H:%M")
        return appointment_time
    except:
        return False

def service_to_id(service_id):
    company_services = dbservice.list_main_services(company_id)
    for company_service in company_services:
        if company_service['id']==service_id:
            service = company_service['info']['title']
            return service
        return str(service_id)
#------------ Copied from bot_service
    
def getNameOfWeek(n):
    if n == 0:
        return 'Monday'
    if n == 1:
        return 'Tuesday'
    if n == 2:
        return 'Wednesday'
    if n == 3:
        return 'Thursday'
    if n == 4:
        return 'Thursday'
    if n == 5:
        return 'Saturday'
    if n == 6:
        return 'Sunday'

def get_valid_slots_by_day(start_apt_date, days_of_week):
    day_name = getNameOfWeek(start_apt_date.weekday()).lower()
    for item in days_of_week:
        if item['title'].lower() == day_name:
            final_slots = []
            for timerange in item['timings']:
                start_date_time = datetime.combine(start_apt_date.date(), time.fromisoformat(timerange['start']))
                end_date_time = datetime.combine(start_apt_date.date(), time.fromisoformat(timerange['end']))
                while start_date_time + dt.timedelta(minutes=DURATION) <= end_date_time:
                      final_slots.append(start_date_time)
                      start_date_time = start_date_time + dt.timedelta(minutes=DURATION)

            return final_slots

    return []

def get_available_slots(date_of_interest,appointments, working_days, exception_dates, duration=30):
    
    available_slots = get_valid_slots_by_day(date_of_interest,working_days['info']['days'])
    final_slots = []
    if len(available_slots) > 0:
        for slot in available_slots:
            available_slot_start_time = slot + dt.timedelta(minutes=1)
            available_slot_end_time = slot + dt.timedelta(minutes=DURATION - 1)
            time_range1 = DateTimeRange(available_slot_start_time, available_slot_end_time)
            is_available = True
            for appointment in appointments:
                    start_time = appointment['appointment_date'] 
                    end_time =   appointment['appointment_date'] + dt.timedelta(minutes=DURATION)
                    time_range2 = DateTimeRange(start_time,end_time) 
                    if time_range1.intersection(time_range2).start_datetime != None:
                       is_available = False
                       break
                    for exc_date in exception_dates:
                        start_time = exc_date['exception_from_date'] 
                        end_time =   exc_date['exception_to_date'] 
                        time_range2 = DateTimeRange(start_time,end_time) 
                        if time_range1.intersection(time_range2).start_datetime != None:
                            is_available = False
                            break
            if is_available:
                final_slots.append(slot)
                

    return final_slots

def get_available_slots_by_date(date_of_interest, service_def_id):
    appointments = dbservice.list_valid_appointments_by_date(3,date_of_interest)
    exception_dates = dbservice.list_service_working_hrs_exception_by_date(service_def_id, date_of_interest)
    working_days = dbservice.list_service_working_days(service_def_id)
    slots = get_available_slots(date_of_interest,appointments, working_days, exception_dates, duration=30)
    return slots


