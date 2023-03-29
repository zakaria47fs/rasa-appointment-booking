from re import split
import psycopg2
from psycopg2.extras import Json
import logging
from logging import Logger
from datetime import datetime
class DbService:
    def __init__(self): 
        print('init')

        
    def get_connection(self):
        return  psycopg2.connect(database="appdemodb",
                        host="database-instance-1.c9wqtksfrpd6.us-east-1.rds.amazonaws.com",
                        user="postgres",
                        password="coffeecaketv",
                        port="5432")


    def list_companies(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT id, title, active FROM company' )
        
        records = cursor.fetchall()
        cursor.close()
        if not connection.closed:
            connection.close()
        return records

    def insert_company(self, title, active=True):
        connection = self.get_connection()
        cursor = connection.cursor()
        record = (title,active)
        results = cursor.execute("INSERT INTO company (title,active) VALUES (%s, %s)",record)
        connection.commit()
        cursor.close()
        if not connection.closed:
            connection.close()

        return results


    ############ service definition ######################
    def list_main_services(self, company_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT id,company_id,title, active, info FROM service_definition where company_id = %s',(str(company_id)) )
        results = cursor.fetchall()
        cursor.close()
        if not connection.closed:
            connection.close()
        main_services = []
        for item in results:     
            service = {'id': item[0], 'company_id': item[1],
            'title': item[2], 'active':item[3], 'info':item[4]}
            main_services.append(service)
        return main_services

        return results

    def insert_service_definition(self,company_id, title, active, info):
        connection = self.get_connection()
        cursor = connection.cursor()
        record = (str(company_id), title, active, Json(info))
        results = cursor.execute("INSERT INTO service_definition  \
        (company_id,title, active, info) VALUES (%s, %s, %s,%s::json)",record)
        connection.commit()
        cursor.close()
        if not connection.closed:
            connection.close()

        return results

    def update_service_definition(self, id, title, active, info):
        try:
            query = """UPDATE service_definition SET 
            title = %s, 
            active = %s,
            info = %s::json 
            where id = %s
            """
            connection = self.get_connection()
            cursor = connection.cursor()

            record = (title, active,Json(info), str(id))
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            if not connection.closed:
                connection.close()

            return "success"
        except Exception as e: 
            Logger.debug(e, exc_info=True)

            return -1

    def delete_service_definition(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        results = cursor.execute("delete from service_definition where   \
        id = %s",(str(id)))
        connection.commit()
        cursor.close()
        if not connection.closed:
            connection.close()

        return results

################## service ##############################
    def list_services(self, service_def_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT id,service_def_id, title,active,info FROM service where service_def_id = %s',(str(service_def_id)) )
        results = cursor.fetchall()
        cursor.close()
        if not connection.closed:
            connection.close()
        services = []
        for item in results:     
            service = {'id': item[0], 'service_def_id': item[1],
            'title': item[2], 'active':item[3], 'info':item[4]}
            services.append(service)
        return services


    def insert_service(self,service_def_id, title,active, info):
        connection = self.get_connection()
        cursor = connection.cursor()
        record = (service_def_id, title,active,Json(info))
        results = cursor.execute("INSERT INTO service (service_def_id, title,active,info) VALUES (%s, %s, %s, %s::json)",record)
        connection.commit()
        cursor.close()
        if not connection.closed:
            connection.close()

        return results

    def update_service(self, id, title, active, info):
        #try:
            query = """UPDATE service set 
            title = %s, 
            active = %s,
            info = %s::json
            where id = %s
            """
            connection = self.get_connection()
            cursor = connection.cursor()

            record = (title,active, Json(info),str(id))
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            if not connection.closed:
                connection.close()

            return "success"
        #except (Exception): 
            print(Exception.__traceback__)
            return -1

    def delete_service(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        results = cursor.execute("delete from service where   \
        id = %s",(str(id)))
        connection.commit()
        cursor.close()
        if not connection.closed:
            connection.close()

        return results


########## wordking days and exceptions #############################

    def insert_service_working_days(self,service_def_id, info):
        connection = self.get_connection()
        cursor = connection.cursor()
        record = (service_def_id, Json(info))
        results = cursor.execute("INSERT INTO service_working_days (service_def_id, info) VALUES (%s, %s::json)",record)
        connection.commit()
        cursor.close()
        if not connection.closed:
            connection.close()

    def update_service_working_days(self, service_def_id, info):
        #try:
            query = """UPDATE service_working_days set 
            info = %s::json
            where service_def_id = %s
            """
            connection = self.get_connection()
            cursor = connection.cursor()

            record = (Json(info),str(service_def_id))
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            if not connection.closed:
                connection.close()

            return "success"
        #except (Exception): 
            print(Exception.__traceback__)
            return -1


    def list_service_working_days(self, service_def_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT service_def_id, info FROM service_working_days where service_def_id = %s',(str(service_def_id)) )
        result = cursor.fetchone()
        cursor.close()
        if not connection.closed:
            connection.close()

        if len(result) > 0:
            return {'service_def_id':result[0],'info':result[1]}
        return None


    def list_service_working_hrs_exception(self, service_def_id):
        
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT id, service_def_id,exception_from_date, exception_to_date, exception_type  FROM working_hrs_exception where service_def_id = %s',(str(service_def_id)) )
        results = cursor.fetchall()
        cursor.close()
        if not connection.closed:
            connection.close()
        return results
    def list_service_working_hrs_exception_by_date(self, service_def_id, date_of_interest):
        connection = self.get_connection()
        cursor = connection.cursor()
        record = (str(service_def_id), date_of_interest)
        cursor.execute('SELECT id, service_def_id,exception_from_date, exception_to_date, exception_type  FROM working_hrs_exception where service_def_id = %s and exception_from_date::date = %s::date  ',record )
        results = cursor.fetchall()
        cursor.close()
        if not connection.closed:
            connection.close()

        exceptions = []
        for item in results:     
            apt = {'id': item[0], 'service_def_id': item[1],
            'exception_from_date': item[2], 'exception_to_date':item[3], 'exception_type':item[4]}
            exceptions.append(apt)
        return exceptions

    
    ## type 1 for unavailable slot type = 2 additional available slot
    def insert_working_hrs_exception(self,service_def_id, from_datetime, to_datetime,excep_type=1):



        connection = self.get_connection()
        cursor = connection.cursor()
        record = (service_def_id, 
        psycopg2.Timestamp(from_datetime.year, from_datetime.month, from_datetime.day, from_datetime.hour,from_datetime.minute), 
        psycopg2.Timestamp(to_datetime.year, to_datetime.month, to_datetime.day, to_datetime.hour,to_datetime.minute), 
        excep_type

        )

        
        results = cursor.execute("INSERT INTO working_hrs_exception (service_def_id, exception_from_date, exception_to_date, exception_type) VALUES (%s, %s,%s,%s)",record)
        connection.commit()
        cursor.close()
        if not connection.closed:
            connection.close()
        
    def delete_working_hrs_exception(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        results = cursor.execute("delete from working_hrs_exception where   \
        id = %s",(str(id)))
        connection.commit()
        cursor.close()
        if not connection.closed:
            connection.close()

        return results

    ######################################### appointment #####################
    def insert_appointment(self,service_def_id,customer_name, customer_phone, appointment_date,status=1):



        connection = self.get_connection()
        cursor = connection.cursor()
        record = (
        service_def_id, 
        customer_name, 
        customer_phone,
        psycopg2.Timestamp(appointment_date.year,appointment_date.month,appointment_date.day, appointment_date.hour, appointment_date.minute), 
        status

        )

        
        results = cursor.execute("INSERT INTO appointment (service_def_id, customer_name, customer_phone, appointment_date, status) VALUES (%s, %s,%s,%s,  %s)",record)
        connection.commit()
        cursor.close()
        if not connection.closed:
            connection.close()

    def list_valid_appointments_by_date(self, service_def_id, from_date):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = 'SELECT id, service_def_id,customer_name, customer_phone, appointment_date from appointment where service_def_id = %s'  \
        'and appointment_date::date = %s::date and status = 1'
        record = (
        service_def_id, 
        psycopg2.Date(from_date.year,from_date.month,from_date.day), 

        )
        cursor.execute(query,record )
        results = cursor.fetchall()
        cursor.close()
        if not connection.closed:
            connection.close()

        appointments= []
 
        for item in results:     
            apt = {'id': item[0], 'service_def_id': item[1],
            'customer_name': item[2], 'customer_phone':item[3], 'appointment_date':item[4]}
            appointments.append(apt)
        return appointments
    def list_valid_appointments_by_phone(self, service_def_id, from_date,customer_phone):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = 'SELECT id, service_def_id,customer_name, customer_phone, appointment_date from appointment where service_def_id = %s'  \
        'and appointment_date::date >= %s::date and customer_phone = %s and status = 1'
        record = (
        service_def_id, 
        psycopg2.Timestamp(from_date.year,from_date.month,from_date.day, from_date.hour, from_date.minute),
        customer_phone 

        )
        cursor.execute(query,record )
        results = cursor.fetchall()
        cursor.close()
        if not connection.closed:
            connection.close()

        appointments= []
 
        for item in results:     
            apt = {'id': item[0], 'service_def_id': item[1],
            'customer_name': item[2], 'customer_phone':item[3], 'appointment_date':item[4]}
            appointments.append(apt)
        return appointments

    def list_customer_valid_appointments_by_phone(self, from_date,customer_phone):
            connection = self.get_connection()
            cursor = connection.cursor()
            query = 'SELECT id, service_def_id,customer_name, customer_phone, appointment_date from appointment where '  \
            'appointment_date::date >= %s::date and customer_phone = %s and status = 1'
            record = (
            psycopg2.Timestamp(from_date.year,from_date.month,from_date.day, from_date.hour, from_date.minute),
            customer_phone 

            )
            cursor.execute(query,record )
            results = cursor.fetchall()
            cursor.close()
            if not connection.closed:
                connection.close()

            appointments= []
    
            for item in results:     
                apt = {'id': item[0], 'service_def_id': item[1],
                'customer_name': item[2], 'customer_phone':item[3], 'appointment_date':item[4]}
                appointments.append(apt)
            return appointments



    def list_valid_appointments_by_datetime(self, service_def_id, from_date):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = 'SELECT id, service_def_id,customer_name, customer_phone, appointment_date from appointment where service_def_id = %s'  \
        'and appointment_date::timestamp = %s::timestamp and status = 1'
        record = (
        service_def_id, 
        psycopg2.Timestamp(from_date.year,from_date.month,from_date.day, from_date.hour, from_date.minute)

        )
        cursor.execute(query,record )
        results = cursor.fetchall()
        cursor.close()
        if not connection.closed:
            connection.close()

        appointments= []
 
        for item in results:     
            apt = {'id': item[0], 'service_def_id': item[1],
            'customer_name': item[2], 'customer_phone':item[3], 'appointment_date':item[4]}
            appointments.append(apt)
        return appointments

    def update_appointment_status(self, id, status):
        #try:
            query = """UPDATE appointment set 
            status = %s
            where id = %s
            """
            connection = self.get_connection()
            cursor = connection.cursor()

            record = (status,str(id))
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            if not connection.closed:
                connection.close()

            return "success"
        #except (Exception): 
            print(Exception.__traceback__)
            return -1

############ suggestions ######################
    def insert_suggestion(self,company_id,customer_name, customer_phone, suggestion_text):

        try:
            current_date = datetime.now()
            connection = self.get_connection()
            cursor = connection.cursor()
            record = (
            company_id, 
            customer_name, 
            customer_phone,
            suggestion_text,
            psycopg2.Timestamp(current_date.year,current_date.month,current_date.day, current_date.hour, current_date.minute)
            )

            
            results = cursor.execute("INSERT INTO suggestion (company_id, customer_name, customer_phone, suggestion_text,date_received) VALUES (%s, %s,%s,%s,  %s::timestamp)",record)
            connection.commit()
            cursor.close()
            if not connection.closed:
                connection.close()
            return 1
        except Exception as e: 
            print(e)
            return -1

    def list_suggestions(self, company_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = 'SELECT id, company_id,customer_name, customer_phone, suggestion_text,date_received from suggestion where company_id = %s'  
        
        record = (
        str(company_id)
        )
        cursor.execute(query,record )
        results = cursor.fetchall()
        cursor.close()
        if not connection.closed:
            connection.close()

        suggestions= []
 
        for item in results:     
            suggestion = {'id': item[0], 'company_id': item[1],
            'customer_name': item[2], 'customer_phone':item[3], 'suggestion_text':item[4], 'date_received':item[5]}
            suggestions.append(suggestion)
        return suggestions

############ promotions ######################

    def insert_promotion(self,company_id,title, promotion_text, active):

        try:
            current_date = datetime.now()
            connection = self.get_connection()
            cursor = connection.cursor()
            record = (
            company_id, 
            title, 
            promotion_text,
            active
            )

            results = cursor.execute("INSERT INTO promotion (company_id, title, promotion_text, active) VALUES (%s, %s,%s,%s)",record)
            connection.commit()
            cursor.close()
            if not connection.closed:
                connection.close()
            return 1
        except Exception as e: 
            print(e)
            return -1

    def list_valid_promotions(self, company_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = 'SELECT id, company_id, title, promotion_text, active from promotion where company_id = %s and active = 1'  
        
        record = (
        str(company_id)
        )
        cursor.execute(query,record )
        results = cursor.fetchall()
        cursor.close()
        if not connection.closed:
            connection.close()

        promotions= []
 
        for item in results:     
            promotion = {'id': item[0], 'company_id': item[1],
            'title': item[2], 'promotion_text':item[3], 'active':item[4]}
            promotions.append(promotion)
        return promotions










    

