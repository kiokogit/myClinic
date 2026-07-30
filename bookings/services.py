from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import exceptions, serializers


from bookings.models import AppointmentsModel
from hrm.services import AvailabilityService
from utils.exceptions import UnauthorizedActorError, UserInputValidationError

# Create your views here.

class BookingService:

    def check_slot_is_available(self, doctor_id, date_time):
        # date
        date = date_time.split(" ")[0]
        available_slots = AvailabilityService().get_doctor_available_slots(doctor_id, date)

        time_slot = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
        
        if str(time_slot) in available_slots:
            return True
        return False

    def cancel_appointment(self, request, appoint_id):

        if request.data.get('remarks', None) in ['', None]:
            raise UserInputValidationError("Cancellation reasons or remarks are required")
        
        cancel_info = AppointmentsModel.objects.filter(pk=appoint_id, status='PENDING').first()
        if not cancel_info:
            raise UserInputValidationError("Appointment is either not found or is invalid")
        if cancel_info.patient != request.user:
            raise UnauthorizedActorError()
        if cancel_info.start_time < datetime.now() - timedelta(minutes=30): # past appointments cannot be cancelled;
            raise UserInputValidationError("Invalid appointment to cancel.")
        cancel_info.status = 'CANCELLED'
        cancel_info.save(update_fields=['last_modified', 'status'])

        cancel_info.remarks.create(  # type:ignore
            remark=request.data.get('remarks'), # type:ignore
            remark_for="APPOINTMENT_CANCELLATION"
        )

        # TODO: Notify the doctor
        return True

    
    def reschedule_appointment(self, request, appoint_id):

        if not request.data.get('start_time', None):
            raise UserInputValidationError("Start time is required.")

        if request.data.get('remarks', None) in ['', None]:
            raise UserInputValidationError("Rescheduling reasons or remarks are required")

        booking_date = datetime.strptime(request.data.get('start_time'), "%Y-%m-%d %H:%M")

        if booking_date < timezone.now() + timedelta(minutes=60):
            raise UserInputValidationError("Appointment booking time must be at least 1 hour from now")
                
        resc_info = AppointmentsModel.objects.filter(pk=appoint_id, status='PENDING').first()
        if not resc_info:
            raise UserInputValidationError("Appointment not found")
        if resc_info.patient != request.user:
            raise UnauthorizedActorError()
        if resc_info.start_time < datetime.now() - timedelta(minutes=60): 
            raise UserInputValidationError("Invalid appointment to reschedule")
        
        if not self.check_slot_is_available(resc_info.doctor.id, str(booking_date)):
            raise UserInputValidationError("The selected appointment time is not available. Please try a different time slot")

        resc_info.start_time = booking_date
        resc_info.save(update_fields=['last_modified', 'start_time'])

        # TODO: Notify the doctor

        resc_info.remarks.create(  # type:ignore
            remark=request.data.get('remarks'), # type:ignore
            remark_for="APPOINTMENT_RESCHEDULING"
        )

        
        return True

