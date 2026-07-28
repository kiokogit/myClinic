
# INTRODUCTION

## Overview

This app handles patient appointments.

- For authentication see the [ACL AND USER MANAGEMENT](#tag/user-management) tag
- To manage doctors availability see [Resource Management](#tag/resource-management)
- Full booking flow is documented under [Appointments](#tag/appointments)

## System Requirements

- Small clinic with 5 doctors
- User to book a 30min appointment slot
- Patient be able to cancel an appointment
- Unbooked/cancelled slots to be available for any other booking

## Design Specifications

These are the required specific functionalities derived from the basic requirements

### Public Side system

- This is the client/patient side accessed for booking of appointments
- Have a Registration/Login/Authentication system, for the user of type 'public' -- role based authentication
- Be able to view all upcoming (self) appointments or bookings -- based on the logged in user
- Can view all available time slots for a specific doctor in a given date -- so all slots sohuld be by date, and by doctor; or by doctor then by date
- Can view and search for a doctor, then see their available slots for booking
- Be able to book appointments (at least 30 mins after now)
- Be able to cancel an appointment that has not yet arrived -- cancelling resets the slot to available
- Be able to reschedule an appointment (edit an appointment) -- to any time in the future

### Actor (Doctor's) side system

- This is the docto's side
- Have authentication/reset system for user type 'doctor'
- View all current/future appointments -- filters be by date, or week or month or all
- View list of available days/slots for scheduling
- Be able to update availability in any time slot, by defining when available (besides administrative functions)
- Also, update an appointment as fulfilled

### Internal (HR/SYSTEM ADMIN) system side

- There's need for a systems admin or human resource side of the system
- Have authentication/login/registration for user type 'in-charge'
- View all appointments by date/time
- View all doctors
- View all registered users by category
- View all doctors details - including subinformation on appoimtnents, cancellations, availability
- Upload doctors' schedule: availability, shifts (day/night), leave days, assigned-other-duties days and other working schedules like lunch hours etc
- revoke doctor's credentials once not in the hospital
- Power to revoke/suspend user if in misuse of the sytem (like a cyber attack, or too many bookings wih no show up)
- Ask user to reschedule (incase there is a problem with the chosen slot - eg overlooked leave day for a doctor)

## Design Assumptions

1. No repeating bookings - That is, no control of user booking same doctor two consecutiec slots
2. Each appointment is only for 30mins slot, not more, not less
3. Patient can book any number of slots, including subsequent slots, with any doctor, same or different
4. No leave can be made on a booked time slot, to cancel the appointment.

## System design considerations

1. No overlapping appointments. No possibility of bookings at the same time by different users (Requires fast endpoints, or quick succession update of time-slots status)
2. Public user cannot see other users' bookings. Only unavailability of the slot. Their appointments can be loaded though.

## System Design Recommendations

1. JWT Bearer tokens Authentication for session management
2. Login/Authentication system using other providers if availble for easy user experience (like google)
3. Aunthentication using OTP, especially for staff (doctors and admin)
4. Rate limiting for public users - to control
5. ACID enforcement using transactions locking etc
6. Auto-update of slots status (script? or socket?)
7. Use PostgreSQL for db -- Well, popular, resilient, opensource, and well relational. Mysql would do similarly anyway
8. Django REST for backend. Go is faster, but for co-routines. I actually want to avoid co-routines. And FASTAPI-- just fast. No much. Well, long setup and basic configurations will take time
9. Status codes used will be the normal ones, nothing custom for now

## Depoyments

- Github for respository and code management
- Using some linode EC2 isntance Available, for testing works
- Autodeploy using docker

## AI Reflections

- Use AI for boilerplate codebase
- Use AI for other design suggestions for data secutiry and authentications
- Use AI for checking for code smells / vulnerabilities
- Use AI for writing tests
- Use AI to suggest best code structure for scalable system design
- Use AI for generating prpoper documentation


## Extra Deiverables

1. A DOCUMENTATION TESTABLE
2. ENDPOINTS EXPORTABLE COLLECTION
3. A small UI?? if available time
