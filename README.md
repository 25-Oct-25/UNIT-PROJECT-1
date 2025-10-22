# Car Importer's Toolkit

## Overview

This is a command-line (CLI) application that functions as a digital showroom and management tool for an imported car business. The system has two main users: the **Admin** (the store manager) and the **Guest** (the customer). Each user has a distinct set of tasks they can perform for the store to function properly.

The Admin manages the inventory, while the Guest can browse available cars, get AI-powered financial advice, and purchase vehicles.

## Features & User Stories

### As an Admin, I should be able to do the following:

* Log in to the system securely with a username and password.
* Add a new car profile to the inventory (which is automatically marked as "For Sale").
* View the *entire* inventory of cars, including those already "Sold".
* Update the price of any car in the inventory.
* Calculate the detailed import cost for any car.
* Get an AI-powered deal analysis for any car in the inventory.
* Save the AI analysis as a formatted PDF report, which is automatically stored in the `pdf-files` directory.
* Log out of the admin session to return to the guest view.

### As a Guest (Customer), I should be able to do the following:

* Browse all cars that are currently "For Sale".
* View detailed product info (Make, Model, Year, Price, Origin) in a clean table.
* Purchase a car, which removes it from the "For Sale" listing by marking it as "Sold".
* Get AI-powered financial advice (deal analysis) on any *available* car.
* Save the AI analysis as a PDF report for review.
* Attempt to log in as an Admin.
* Exit the application.



## Usage
First you need to export your GOOGLE_API_KEY like this :
* on macOS:
```bash
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```
* on Windows:
```bash
set GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

Then, start the application by running `main.py` from your terminal:

```bash
python main.py
```
### Guest Usage:
* `type in 1` to access the Admin login prompt.
* `type in 2` to browse all cars currently available for sale.
* `type in 3` to view the list of available cars and purchase one.
* `type in 4` to get an AI analysis on an available car.
* `type in 5` to exit the application.

### Admin Usage: 
* `type in 1` to add a new car to the inventory.
* `type in 2` to view all cars in the system (both "For Sale" and "Sold").
* `type in 3` to calculate the detailed import cost for any car.
* `type in 4` to get an AI analysis on any car.
* `type in 5` to update the price of a car.
* `type in 6` to log out and return to the Guest menu.
