import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from django.utils import timezone
from django.test import TestCase

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

# Adjust the import paths according to your project structure
from bookings.api import AppointmentsView


# Adjust the import paths according to your project structure
from bookings.services import BookingService
from utils.exceptions import UserInputValidationError, UnauthorizedActorError


class TestBookingService(TestCase):
    def setUp(self):
        self.service = BookingService()
        self.mock_request = MagicMock()
        self.mock_user = MagicMock()
        self.mock_request.user = self.mock_user

    @patch('bookings.services.AvailabilityService')
    def test_check_slot_is_available_returns_true(self, mock_avail_service):
        # Setup mock available slots
        instance = mock_avail_service.return_value
        instance.get_doctor_available_slots.return_value = ['14:30', '15:00']

        # Test valid slot
        result = self.service.check_slot_is_available(1, "2026-10-15 14:30:00")
        self.assertTrue(result)
        instance.get_doctor_available_slots.assert_called_with(1, "2026-10-15")

    @patch('bookings.services.AvailabilityService')
    def test_check_slot_is_available_returns_false(self, mock_avail_service):
        instance = mock_avail_service.return_value
        instance.get_doctor_available_slots.return_value = ['14:30', '15:00']

        # Test invalid slot
        result = self.service.check_slot_is_available(1, "2026-10-15 16:00:00")
        self.assertFalse(result)

    def test_cancel_appointment_missing_remarks(self):
        self.mock_request.data = {'remarks': ''}
        
        with self.assertRaisesMessage(UserInputValidationError, "Cancellation reasons or remarks are required"):
            self.service.cancel_appointment(self.mock_request, 1)

    @patch('bookings.services.AppointmentsModel.objects.filter')
    def test_cancel_appointment_not_found(self, mock_filter):
        self.mock_request.data = {'remarks': 'No longer needed'}
        mock_filter.return_value.first.return_value = None
        
        with self.assertRaisesMessage(UserInputValidationError, "Appointment is either not found or is invalid"):
            self.service.cancel_appointment(self.mock_request, 1)

    @patch('bookings.services.AppointmentsModel.objects.filter')
    def test_cancel_appointment_unauthorized_user(self, mock_filter):
        self.mock_request.data = {'remarks': 'No longer needed'}
        mock_appt = MagicMock()
        mock_appt.patient = "different_user"
        mock_filter.return_value.first.return_value = mock_appt
        
        with self.assertRaises(UnauthorizedActorError):
            self.service.cancel_appointment(self.mock_request, 1)

    @patch('bookings.services.AppointmentsModel.objects.filter')
    def test_cancel_appointment_success(self, mock_filter):
        self.mock_request.data = {'remarks': 'No longer needed'}
        mock_appt = MagicMock()
        mock_appt.patient = self.mock_user
        # Ensure it's in the future so it doesn't fail the time check
        mock_appt.start_time = datetime.now() + timedelta(days=1) 
        mock_filter.return_value.first.return_value = mock_appt

        result = self.service.cancel_appointment(self.mock_request, 1)
        
        self.assertTrue(result)
        self.assertEqual(mock_appt.status, 'CANCELLED')
        mock_appt.save.assert_called_with(update_fields=['last_modified', 'status'])
        mock_appt.remarks.create.assert_called_with(
            remark='No longer needed', 
            remark_for="APPOINTMENT_CANCELLATION"
        )

    def test_reschedule_appointment_missing_start_time(self):
        self.mock_request.data = {'remarks': 'Change of plans'}
        with self.assertRaisesMessage(UserInputValidationError, "Start time is required."):
            self.service.reschedule_appointment(self.mock_request, 1)

    def test_reschedule_appointment_invalid_booking_time(self):
        # Try to book 10 minutes from now (must be >= 60 mins)
        invalid_time = (timezone.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        self.mock_request.data = {'start_time': invalid_time, 'remarks': 'Change of plans'}
        
        with self.assertRaisesMessage(UserInputValidationError, "Appointment booking time must be at least 1 hour from now"):
            self.service.reschedule_appointment(self.mock_request, 1)

    @patch.object(BookingService, 'check_slot_is_available')
    @patch('bookings.services.AppointmentsModel.objects.filter')
    def test_reschedule_appointment_success(self, mock_filter, mock_check_slot):
        valid_time = (timezone.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        self.mock_request.data = {'start_time': valid_time, 'remarks': 'Change of plans'}
        
        mock_appt = MagicMock()
        mock_appt.patient = self.mock_user
        mock_appt.start_time = datetime.now() + timedelta(days=1)
        mock_filter.return_value.first.return_value = mock_appt
        mock_check_slot.return_value = True

        result = self.service.reschedule_appointment(self.mock_request, 1)

        self.assertTrue(result)
        mock_appt.save.assert_called_with(update_fields=['last_modified', 'start_time'])
        mock_appt.remarks.create.assert_called_with(
            remark='Change of plans', 
            remark_for="APPOINTMENT_RESCHEDULING"
        )


class TestAppointmentsView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.mock_user = MagicMock()
        self.mock_user.is_authenticated = True

    @patch('bookings.api.AppointmentsView.get_permissions')
    @patch('bookings.api.AppointmentsView.queryset')
    def test_get_queryset_public_user(self, mock_queryset, mock_perms):
        # Simulate public user
        self.mock_user.user_type = 'public'
        self.client.force_authenticate(user=self.mock_user)

        view = AppointmentsView()
        view.request = MagicMock()
        view.request.user = self.mock_user
        view.queryset = mock_queryset

        view.get_queryset()
        mock_queryset.filter.assert_called_with(patient=self.mock_user)

    @patch('bookings.api.AppointmentsView.queryset')
    def test_get_queryset_doctor_user(self, mock_queryset):
        # Simulate doctor user
        self.mock_user.user_type = 'doctor'
        
        view = AppointmentsView()
        view.request = MagicMock()
        view.request.user = self.mock_user
        view.queryset = mock_queryset

        view.get_queryset()
        mock_queryset.filter.assert_called_with(doctor=self.mock_user)

    # @patch('bookings.api.BookingService.cancel_appointment')
    # def test_cancel_endpoint(self, mock_cancel_service):
    #     self.client.force_authenticate(user=self.mock_user)
        
    #     # Bypass DRF permissions strictly for testing the view action logic
    #     with patch('bookings.api.AppointmentsView.get_permissions', return_value=[]):
    #         response = self.client.patch('/appointments/1/cancel/', {'remarks': 'test'})
            
    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertEqual(response.data['detail'], "Cancellation has been successful")
    #         mock_cancel_service.assert_called_once()

    # @patch('bookings.api.BookingService.reschedule_appointment')
    # def test_reschedule_endpoint(self, mock_reschedule_service):
    #     self.client.force_authenticate(user=self.mock_user)
        
    #     with patch('bookings.api.AppointmentsView.get_permissions', return_value=[]):
    #         payload = {'start_time': '2026-10-15 14:30:00', 'remarks': 'test'}
    #         response = self.client.patch('/appointments/1/reschedule/', payload)
            
    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertEqual(response.data['details'], "Appointment has been rescheduled successful")
    #         mock_reschedule_service.assert_called_once()