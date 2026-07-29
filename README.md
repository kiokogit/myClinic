
# INTRODUCTION

## Overview

This app handles patient appointments.

- For authentication see the [ACL AND USER MANAGEMENT](#tag/user-management) tag
- To manage doctors availability see [Resource Management](#tag/resource-management) tag
- Full booking flow is documented under [Appointments](#tag/appointments) tag

## Useful Links

- View Backend Server Demo live on [Render Here](https://myclinic-fpvm.onrender.com)
- PLEASE NOTE: RENDER.COM DEPLOYMENTS TAKE A WHILE ON FREE TIER SERVERS. HANG-IN-THERE. OR JUST [Buy me a droplet!](https://cloud.digitalocean.com/suspended?i=cff77e) :>)
- View this documentation, and API Endpoints on Scalar from [this link](https://kiokogit-myclinic.apidocumentation.com/)

## Getting started Locally

- Clone the repository locally from [this Github Repository](https://github.com/kiokogit/myClinic.git)
- Create a virtual environment: ```python -m venv .venv``` and activate it
- Run ```pip install -r requirements.txt```
- Run Migrations for your database set up ```python manage.py migrate```
- Start server by running ```python manage.py runserver```
- Access Dynamic Scalar documentation through ```http://localhost:8000/api/docs```

- For more information access documentation [links here](https://kiokogit-myclinic.apidocumentation.com/)

## System Requirements

- Small clinic System with 5 doctors
- User (Patient) to book a 30min appointment slot
- Patient be able to cancel an appointment
- Unbooked/cancelled slots to be available for any other booking

## Design Specifications

These are the required specific functionalities derived from the basic requirements

### 1. Public Side system

- This is the client/patient side accessed for booking of appointments
- Have a Registration/Login/Authentication system, for the user of type 'public' -- role based authentication
- Be able to view all upcoming (self) appointments or bookings -- based on the logged in user
- Can view all available time slots for a specific doctor in a given date -- so all slots sohuld be by date, and by doctor; or by doctor then by date
- Can view and search for a doctor, then see their available slots for booking
- Be able to book appointments (at least 30 mins after now)
- Be able to cancel an appointment that has not yet arrived -- cancelling resets the slot to available
- Be able to reschedule an appointment (edit an appointment) -- to any time in the future

### 2. Actor (Doctor's) side system

- This is the docto's side
- Have authentication/reset system for user type 'doctor'
- View all current/future appointments -- filters be by date, or week or month or all
- View list of available days/slots for scheduling
- Be able to update availability in any time slot, by defining when available (besides administrative functions)
- Also, update an appointment as fulfilled

### 3. Internal (HR/SYSTEM ADMIN) system side

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

## System Design Recommendations (TODOs not yet Done)

1. JWT Bearer tokens Authentication for session management
2. Login/Authentication system using other providers if availble for easy user experience (like google)
3. Aunthentication using OTP, especially for staff (doctors and admin)
4. Rate limiting for public users - to control multiple-booking issues, etc
5. ACID enforcement using transactions locking etc
6. Auto-update of slots status (script? or socket?)
7. Use PostgreSQL for db -- Well, popular, resilient, opensource, and well relational. Mysql would do similarly anyway
8. Django REST for backend. Go is faster, but for co-routines. I actually want to avoid co-routines. And FASTAPI-- just fast. No much. Well, long setup and basic configurations will take time
9. Status codes used will be the normal ones, nothing custom for now

## System Data Modelling

The data flow for the system will be as follows

1. User model manages all types of user, from doctors, public and admins
2. hrm.models keep records of working schedules per doctor, added by an admin. Unavailability slots and leaves are taken and recorded here
3. bookings app models keep track of appointment activity for the patient and for the doctor as well
4. system models store logs and errors captured through error handlers available

## URLS

- All routers are automatically discovered in the app. This will help control apps that are broken from appearing
- Also, adding new ones do not affect the others. Clean code too

## How It Works

This application works in the following flow:

Authentication:

- Public user (patient or client) registers and logs in through the provided authentication mechanism
- Authentication is performed using JWT tokens signed and using a secret signature and H256 algorithm
- A system user (or admin or HR staff) has an account created by the superuser account for management of the system activity
- The Admin creates an account for the Doctors (no direct registration for doctors) and they proceed with their own account management

Schedule management:

- The Admin also adds the specific doctor's schedules - availability (day or night shifts), and unavailability (such as leave days) per day.
- The schedules are described per day and per time_in and time_out durations. This defines a doctor's availability
- There may be unavailability in case a doctor is scheduled, but calls in sick. This is set by the admin as well, and the admin fills in with a 'replacement_doctor' to fill in the schedule
- The admin can see the full schedule (in a calendar format) for each user.

Booking and appointments:

- Each schedule submitted is assummed to contain 30min time slots, beginning at the top of or half past the hour of the defined schedule (To make it simple)
- The public user sees the availability in form of 30min slots;
- The patient who wants to book an appointment searches a doctor, and checks his/her availability of the specific date;
- The patient books a slot with optional remarks (if available). There is further validation of the availability of the slot during booking just incase there is concurrent requests.
- Upon confirmation, the patient can view their make bookings, with date, time and doctor;
- A patient can cancel, or reschedule the appointment (at least 1 hour to the appointment) if they want to, with reasons.

Other Functionalities:

- No appointments can be made to a doctor if not declared as available / on shift that day

## Depoyment & CI/CD

- Github for respository and code management
- Autodeploy on Render.com using a Deploy Hook
- Deployment has been configured using github actions.
- The ```main``` Branch deploys with every merge of a PR
- The pipeline has three stages: 
    1. a testing level that triggers tests and prevents merge of the PR before tests are successful
    2. a main deployment stage that runs on merge of the Pull request.
    3. and a documents deployment stage that runs to autodepoy documentations to Scalar using an API-KEY

- PLEASE NOTE: RENDER.COM DEPLOYMENTS TAKE A WHILE ON FREE TIER SERVERS. HANG-IN-THERE.

## AI Reflections

- Used AI for boilerplate codebase - such as base models, and utils like decode_jwt
- Used AI for other design suggestions for data secutiry and authentications
- Used AI for checking for code smells / vulnerabilities
- Used AI for writing some tests
- Used AI to suggest best code structure for scalable system design
- Used AI for generating proper documentation

## Extra Deiverables

1. A DOCUMENTATION TESTABLE
2. ENDPOINTS EXPORTABLE COLLECTION
3. A small UI?? if available time
