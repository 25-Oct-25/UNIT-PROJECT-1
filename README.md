# UNIT-PROJECT-1

# CourseHub – Interactive Learning CLI

CourseHub is an interactive command-line (CLI) learning platform built in Python.  
It allows students to enroll in courses, track their progress, ask AI questions about the course content,  
and receive a PDF certificate via email upon completion.  
Admins can manage courses and upload resource links for each course.

---

# Features

# Authentication

- Login as Student or Admin (role-based access).
- Case-insensitive email and name (e.g., John@Gmail.com = john@gmail.com).
- Admin PIN: 1234.

# Admin Features

- Add new courses with title, level, price, and summary.
- Add and list resource links for each course (e.g., YouTube videos).
- View all available courses.

# Student Features

- View and enroll in available courses.
- View enrolled courses with progress bars and levels.
- Update progress percentage.
- View course resource links.
- Ask questions to the built-in AI Assistant (Gemini) within the course.
- Generate a PDF certificate and automatically receive it via email with a congratulatory message.
- Get personalized course recommendations.

# AI Integration

The system uses Google Gemini API (google-generativeai) to provide intelligent responses to students' questions inside each course.  
If the quota is exceeded, it automatically falls back to lighter models such as gemini-2.5-flash-lite.

# Email Integration

When a student completes a course, student can request to a PDF certificate is generated and sent via email.

# Developer

Developed by: Abdulrahman Al-Qahtani  
Project: UNIT PROJECT 1 – Tuwaiq Academy  
College: Jubail Industrial College  
Language: Python  
Year: 2025
