from email_validator import validate_email, EmailNotValidError

email_address = "hissah@gmail.com"
try:
    v =validate_email(email_address)
    email = v.email
    print(f"{email} The email is correct.")
except EmailNotValidError as e:
    print(f"{str(e)} the email unvalid")