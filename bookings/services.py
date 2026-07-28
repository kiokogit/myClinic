from datetime import datetime


from hrm.services import AvailabilityService

# Create your views here.

class BookingService:

    def check_slot_is_available(self, doctor_id, date_time):
        # date
        date = date_time.split(" ")[0]
        available_slots = AvailabilityService().get_doctor_available_slots(doctor_id, date)

        print(available_slots)

        time_slot = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
        
        if str(time_slot) in available_slots:
            return True
        return False

    def cancel_appointment(self, appoint_id):


        return True

