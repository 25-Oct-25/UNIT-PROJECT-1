# UNIT-PROJECT-1


## Based on what you’ve learned until now , create a project of your choosing (impress us with your imagination) . This project must at least satisfy the following minimum requirements :

- Must be interactive on CLI.
- Use your coding skills in Python accurately.
- Organize Your Code into modules & (or packages)
- Use git & Github to track changes in your code.

# UNIT-PROJECT-1

## Project: Flight Campaign Manager ✈️

## Overview
A CLI-based flight campaign management system. This project allows users to manage flight campaigns, join campaigns, and track participants. There are 2 main types of users: Leaders and Members. Each user has different functionalities based on their role.

## Features & User Stories

### As a Leader, I should be able to:
- Register and login to the system.
- Add new flight campaigns with details (airline, flight number, departure, destination, max members).
- View all campaigns I have created.
- See the list of members registered for my campaigns.
- Send notifications or emails to campaign members (optional feature).

### As a Member, I should be able to:
- Register and login to the system.
- Browse all available campaigns.
- Join a campaign if slots are available.
- Receive email confirmations for joining a campaign.
- View my participation history.

## Usage
This project is CLI-based. Users interact with it using commands and menu options.

Examples:
- Select `1` for Leader or `2` for Member at the main menu.
- Leaders can register, login, add campaigns, and view members.
- Members can register, login, browse campaigns, and join campaigns.
- Passwords are validated for security (8+ chars, uppercase, lowercase, number).
- Emails are validated for correct format and confirmation notifications are sent automatically.

### Notes
Before submitting or sharing the project, make sure to run:


### For your project. Edit this README.md file to include your own project name,  overview, user stories, and usage. 

### NOTE: before submitting the final project, please do the following command:
`pip freeze > requirements.txt` to enable use to know & use the packages used in your project.
