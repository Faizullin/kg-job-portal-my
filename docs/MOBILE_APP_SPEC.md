### KG Job Portal — Mobile App Technical Specification

This document defines the Flutter mobile application requirements and tasks for developers.

## 1) Backend API overview
- REST API with versioned endpoints
- Token-based authentication
- WebSockets for real-time chat
- JSON data format, multipart for file uploads
- Standard pagination support

## 2) Mobile app stack

### Flutter
- Flutter framework for cross-platform mobile development
- Material Design components
- State management for app logic

### REST API
- HTTP client for backend communication
- REST endpoints for all data operations
- JSON request/response format
- Multipart support for file uploads
- Pagination handling for list endpoints

### WebSocket for chat
- WebSocket connection for real-time messaging
- Persistent connection for chat functionality
- Reconnection handling for network issues
- Offline message queue support

### Authentication
- Firebase Authentication handles user sign-in and sign-up
- After Firebase authentication, exchange Firebase token with backend to receive app token
- App token used for all backend API requests
- Token stored securely on device
- Token refresh mechanism for expired tokens
- Same authentication token used for WebSocket connections

### OpenAPI
- OpenAPI specification file provided by backend
- Use OpenAPI to generate API client code automatically
- Generate data models and request/response types from specification
- Reduces manual API integration work

### Additional components
- FCM for push notifications
- Environment-based configuration for dev/stage/prod environments

## 3) Pages and flows (mobile)
- Onboarding & Auth
  - Splash + maintenance check
  - Onboarding tips (optional)
  - Login (Firebase)
  - Register (Firebase)
  - Forgot/Reset password (Firebase)

- Main user flows
  - Home/Feed: personalized or latest jobs
  - Search: keyword + filters (location, role, salary, type)
  - Job Details: description, company, requirements, actions
  - Apply Flow: attach resume/files, answer questions, submit
  - Saved Jobs: list and manage saved items
  - Applications: status tracking and history
  - Company Profile: details and open roles
  - Profile & Resume: personal info, skills, experience, attachments
  - Notifications: list and deep-link into content
  - Chats: conversation list and message thread (WS-enabled)
  - Settings: theme, language, notifications, sign out, legal

## 4) Authentication flow
- Firebase Authentication for sign-in/sign-up
- Token exchange with backend after Firebase auth
- Secure token storage
- Token refresh handling
- Authentication token for WebSocket connections

## 5) REST API usage
- Connect to backend API endpoints
- Handle pagination and filtering
- Support file uploads
- Error handling for common HTTP errors

## 6) WebSocket chat
- Connect to chat endpoint with authentication
- Send and receive messages
- Support read receipts and unread counts
- Handle connection issues and offline queue

## 7) Maintenance/disable strategy
- Check maintenance status on app launch
- Display maintenance screen when needed
- Block user access during maintenance
- Support minimum app version requirements

## 8) Technical tasks
- Setup Firebase Authentication
- Configure API client
- Build required pages and screens
- Implement WebSocket chat functionality
- Integrate push notifications
- Add maintenance mode support
- Configure environment settings

## 9) Current implementation status

### Existing pages
- Splash screen
- Login screen
- Register screen
- Onboarding screen
- Home screen
- Profile screen
- Edit profile screen
- Notification settings screen
- Language settings screen
- Various other screens exist

### Missing pages (required for job portal)
- Job Search page with filters
- Job Details page
- Job Apply Flow
- Saved Jobs page
- Applications page
- Company Profile page
- Notifications list page
- Chats conversation list
- Chat message thread
- Forgot/Reset password
- Maintenance check on splash
