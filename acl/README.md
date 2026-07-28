# ACL AND USER MANAGEMENT

This now works as a charm.
Manages all users and access control - roles, and groups if available

## Functionalities

### User Authentication

- This includes

1. User Registration
2. User login/Logout
3. User authentication management
4. Role based management

## Registration

- Every user is considered a custom user, with difference in ```user_type``` as either ```Doctor```, ```public``` or ```admin```
- Registration includes sign up using ```password``` and ```email``` as the username
- ```Admin``` and ```Doctor``` users can require OTP if approved

## Login and Authenticaiton management

- User logs in using basic credentials
- Client receives authentication headers/credentials to share with server for athorization
- Otherwise, returns 401 for invalid credentials
- Logout is managed from backend as well, by invalidating login tokens (#TODO)

## Role Based Access Control

- Users are divided by role/ ```user_type``` at the very least.
- Resource access is also managed by user type, with admin having all-area access
