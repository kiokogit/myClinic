from datetime import datetime, timedelta
from bookings.models import AppointmentsModel
from hrm.models import DoctorsWorkScheduleModel, UserUnavailabilityModel

# Create your views here.
class AvailabilityService:

    def get_doctor_available_slots(self, doc_id, book_date):

        if not doc_id or not book_date:
            print('no notihig')
            return []

        try:
            book_date = datetime.strptime(book_date, "%Y-%m-%d").date()
        except ValueError:
            print('value error')
            return []

        if book_date < datetime.now().date():
            print('book date is less')
            return []

        # Doctor away for the whole day?
        if UserUnavailabilityModel.objects.filter(
            doctor_id=doc_id,
            status="ACTIVE",
            start_time__date__lte=book_date,
            end_time__date__gte=book_date,
        ).exists():
            print('user not avialaibe')
            return []

        time_slots = set()

        user_schedules = DoctorsWorkScheduleModel.objects.filter(
            doctor_id=doc_id,
            start_date__lte=book_date,
            end_date__gte=book_date,
        )

        # Fetch only leave entries touching this day
        day_unavailability = UserUnavailabilityModel.objects.filter(
            doctor_id=doc_id,
            status="ACTIVE",
            start_time__date__lte=book_date,
            end_time__date__gte=book_date,
        )

        for schedule in user_schedules:

            current = datetime.combine(book_date, schedule.day_start_time)
            end = datetime.combine(book_date, schedule.day_end_time)

            while current < end:

                slot_end = current + timedelta(minutes=30)

                # Check whether this slot overlaps any leave period
                unavailable = day_unavailability.filter(
                    start_time__lt=slot_end,
                    end_time__gt=current,
                ).exists()

                if not unavailable:
                    time_slots.add(current.strftime("%H:%M"))

                current = slot_end

        # Add slots where this doctor is covering for another doctor
        replacement_shifts = UserUnavailabilityModel.objects.filter(
            replacement_doctor_id=doc_id,
            status="ACTIVE",
            start_time__date__lte=book_date,
            end_time__date__gte=book_date,
        )

        for replacement in replacement_shifts:

            # Restrict the replacement period to the requested day
            shift_start = max(
                replacement.start_time,
                datetime.combine(book_date, datetime.min.time())
            )

            shift_end = min(
                replacement.end_time,
                datetime.combine(book_date + timedelta(days=1), datetime.min.time())
            )

            current = shift_start.replace(
                second=0,
                microsecond=0
            )

            # Round up to the next 30-minute boundary
            if current.minute % 30 != 0:
                current += timedelta(minutes=30 - current.minute % 30)
                current = current.replace(second=0, microsecond=0)

            while current < shift_end:
                time_slots.add(current.strftime("%H:%M"))
                current += timedelta(minutes=30)

        # Remove slots already booked by patients
        booked_slots = set(
            AppointmentsModel.objects.filter(
                doctor__id=doc_id,
                status__in=["PENDING", "ONGOING"],
                start_time__date=book_date,
            ).values_list("start_time", flat=True)
        )
        

        booked_slots = {
            dt.strftime("%H:%M")
            for dt in booked_slots
        }

        time_slots -= booked_slots

        return sorted(time_slots)

    def create_schedule(self, doc_id):
        ...

