from typing import Text, Any, Dict
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import  AllSlotsReset, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from datetime import datetime
from  services.dbconnection import DbService
from utils import service_to_id, get_available_slots_by_date, company_services,  ALL_PROMOTIONS, ALL_SERVICES, appointment_date_formator, appointment_time_validator


dbservice = DbService()
company_id = 3
from_date = datetime.today()
customer_phone = "123456"

class ViewAppointment(Action):
    def name(self):
        return "action_view_appointment"    
    
    def run(self, dispatcher, tracker, domain):
        appointments = dbservice.list_customer_valid_appointments_by_phone(from_date,customer_phone)
        if len(appointments)>1:
            dispatcher.utter_message(text='your appointments are : ')
            for appointment in appointments:
                dispatcher.utter_message(text='-id :' + str(appointment['id'])+ ' for '+service_to_id(appointment['service_def_id']) +' on '+appointment['appointment_date'].strftime("%H:%M"))
        elif len(appointments)==1:
            dispatcher.utter_message(text="your appointment is: " )
            for appointment in appointments:
                dispatcher.utter_message(text='-id :' + str(appointment['id'])+ ' for '+service_to_id(appointment['service_def_id']) +' on '+appointment['appointment_date'].strftime("%H:%M"))
        if len(appointments)==0:
            dispatcher.utter_message(text="you don't have any appointments today" )
            dispatcher.utter_message(text="Any thing else?" )
            return[SlotSet("cancelled_appointment", False) ]
        
class ViewPromotions(Action):
    def name(self):
        return "action_view_promotions"    
    
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="our promotion are : ")
        dispatcher.utter_message(text=', '.join(str(x) for x in ALL_PROMOTIONS))

class ViewOfficeHours(Action):
    def name(self):
        return "action_view_office_hours"    
    
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="our office hours are : ")
        results = dbservice.list_service_working_days(company_id)
        for resultt in results['info']['days']:
            dispatcher.utter_message(text=resultt['title'] + ':' + resultt['timings'][0]['start'] + ' to ' + resultt['timings'][0]['end']+' , '+ resultt['timings'][1]['start'] + ' to ' + resultt['timings'][1]['end'])

class ViewServices(Action):
    def name(self):
        return "action_view_services"    
    
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="our services are : ")
        dispatcher.utter_message(text=', '.join(str(x) for x in ALL_SERVICES))

class ResetSlot(Action):

    def name(self):
        return "action_reset_slot"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]
#----------------------------------------------------

class ValidateBookAppointmentForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_book_appointment_form"

    def validate_service(
    self,
    slot_value: Any,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
) -> Dict[Text, Any]:
        if str(slot_value).lower().strip() not in ALL_SERVICES:
            dispatcher.utter_message(text=f"Unfortunately, we are not offering that service at the moment, sorry for the disappointing news.")
            dispatcher.utter_message(text=' are you interested in : ' + ', '.join(str(x) for x in ALL_SERVICES))
            return {"service": None}
        for service in company_services:
            if service['info']['title']==str(slot_value).lower().strip():
                service_id = service['id']
        return {"service_id": service_id}

    def validate_service_id(
    self,
    slot_value: Any,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
) -> Dict[Text, Any]:
        service = tracker.get_slot("service")
        for services in company_services:
            if services['info']['title']==str(service).lower().strip():
                service_id = services['id']
        return{"service_id": service_id}

    def validate_app_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        service_id = int(tracker.get_slot("service_id"))
        formated_date = appointment_date_formator(slot_value)
        if formated_date==False:
            dispatcher.utter_message(text=f"{slot_value} is not a valid date (allowed date format dd/mm/yy or dd-mm-yy and must be lees than one week from today's date)")
            return {"app_date": None}
        avaliable_date = get_available_slots_by_date(formated_date, service_id)
        if len(avaliable_date)==0:
            dispatcher.utter_message(text=f"we are booked at that date , can you choose another date")
            return {"app_date": None}
        return {"app_date": slot_value}
    
    def validate_app_time(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        service_id = tracker.get_slot("service_id")
        app_date = tracker.get_slot("app_date")
        formated_date = appointment_date_formator(app_date)
        avaliable_times_by_date = get_available_slots_by_date(formated_date, service_id)
        avaliable_times = []
        for avaliable_time_by_date in avaliable_times_by_date:
            avaliable_times.append(avaliable_time_by_date.strftime("%H:%M"))
        is_valide_time = appointment_time_validator(slot_value)
        if is_valide_time==False :
            dispatcher.utter_message(text=f"{slot_value} is not a valid time (allowed time formate 13:00 )")
            return {"app_time": None}
        if is_valide_time.strftime("%H:%M") not in avaliable_times:
            dispatcher.utter_message(text=f"we are booked at that time , you can choose another time from")
            dispatcher.utter_message(text=" ".join(avaliable_times))
            return {"app_time": None}
        return {"app_time": slot_value}
    
class BookAppointment(Action):
    def name(self) -> Text:
        return "action_book_appointment"
    def run(self, dispatcher,tracker, domain):
        service_id = int(tracker.get_slot("service_id"))
        app_date = tracker.get_slot("app_date")
        try: 
            app_date = datetime.strptime(app_date,'%d/%m/%Y')
        except:
            app_date = datetime.strptime(app_date,'%d-%m-%Y')
        app_time = tracker.get_slot("app_time")
        app_time = datetime.strptime(app_time,'%H:%M')
        from_date = datetime(app_date.year,app_date.month,app_date.day,app_time.hour,app_time.minute,app_time.second)
        name = tracker.get_slot("name")
        dbservice.insert_appointment(service_id,name,customer_phone,from_date,1)
        return []

class ValidateCancelForm(FormValidationAction):
        def name(self):
            return "validate_cancel_appointment_form"
        def validate_cancelled_appointment(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
            cancelled_appointment_id = tracker.get_slot("cancelled_appointment")
            appointments = dbservice.list_customer_valid_appointments_by_phone(from_date,customer_phone)
            appointment_ids = []
            for appointment in appointments:                    
                appointment_ids.append(str(appointment['id']))
            if cancelled_appointment_id!=False:
                if slot_value not in appointment_ids:
                    dispatcher.utter_message(text='invalid id choose a valide one')
                    return{"cancelled_appointment": None}
                dispatcher.utter_message(text=f'Your going to cancel appointment {slot_value}')
                dispatcher.utter_message(text='do you submit')
                return{"cancelled_appointment": slot_value} 
            
class CancelAppointment(Action):
    def name(self) -> Text:
        return "action_cancel_appointment"
    
    def run(self, dispatcher, tracker, domain):
        cancelled_appointment_id = tracker.get_slot("cancelled_appointment")
        if cancelled_appointment_id!=None and cancelled_appointment_id!=False:
            dbservice.update_appointment_status(int(cancelled_appointment_id), 3)
        return []

class SubmitSuggestion(Action):
    def name(self) -> Text:
        return "action_submit_suggestion"
    
    def run(self, dispatcher, tracker, domain):
        suggestion = tracker.get_slot("suggestion")
        name = tracker.get_slot("name")
        if suggestion!=None :
            dbservice.insert_suggestion(company_id,name,customer_phone,suggestion)
        return []