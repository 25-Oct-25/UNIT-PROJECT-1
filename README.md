# AI Interactive Story Creator

## Overview
An interactive storytelling application that allows users to create, continue, and manage AI-generated stories directly from the command line.  
Each user can log in, start a new story, choose its genre and length, and shape the story through multiple choices — making every story unique and personalized.

The app connects to the **Hugging Face API** to generate natural, flowing storylines and supports exporting stories as **PDF** files, or even sending them directly via **email**.

---

## Features & User Stories

As a User, I can:

1. Sign up / Log in with a secure password system.  
2. Create new stories with chosen genre and length.  
3. Continue stories based on AI-generated options.  
4. Save my progress and resume later.  
5. View, delete, or export my old stories.  
6. Export a story as a PDF file.  
7. Send my story via email with attachments.

---

## Example Story
Users can write any story they imagine — from dramatic journeys to mysterious adventures — and shape the path through interactive choices.  
Each story evolves based on the user’s decisions, making every playthrough unique.

---

## Setup
Before running the project, make sure you have the following:

1. Create a `.env` file in the project root directory.  
2. Add your credentials:

HUGGINGFACE_API_KEY=your_huggingface_api_key
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
ENCRYPTION_KEY=your_secret_key

3. Run the program in your terminal.

---

## Technologies Used
1. Python  
2. Hugging Face API — AI text generation  
3. ReportLab — PDF exporting  
4. Colorama — CLI color enhancement  
5. smtplib — Email sending  
6. dotenv — Secure credential management

---

Developed for educational and creative purposes.


###  Developed by *[Lama Alharbi]*  
**Interactive Story Project — 2025**

