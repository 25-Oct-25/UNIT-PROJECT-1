# UNIT-PROJECT-1

## PhishSentry Project:

#### Overview : PhishSentry is a security analysis tool designed to detect and evaluate potential phishing domains.The system automatically reads a list of domains from a local file, analyzes them through multiple intelligence layers (DNS, WHOIS, TLS, and similarity analysis), and classifies each domain by risk level — High, Medium, or Safe.PhishSentry aims to help security analysts and researchers quickly identify suspicious domains that mimic legitimate brands.. 

### Features & User Stories
#### As a Security Analyst, I should be able to:
- Load a list of domains from data/domains.txt.
- Load known trusted brands from data/brands.txt.
- Automatically calculate the similarity score between each domain and brand name.
- Perform DNS lookups to gather records such as A, MX, and TXT.
- Collect WHOIS and TLS information when available.
- Detect Fast-Flux behavior (suspicious frequent IP changes).
- View all results directly in the terminal in a clear, color-coded format.
- See the total number of scanned domains and their classification summary at the   end of the scan.


#### Usage :
Type in run to start the full phishing domain analysis.
Type in scan to perform a quick similarity and DNS scan.
Type in report to generate a summary report for a domain.
Type in add brand_name to add a new trusted brand to the system.
Type in remove brand_name to delete a brand from the trusted list.
Example :
> python main.py run
> python main.py scan
> python main.py report google.com
> python main.py add Google
> python main.py remove Amazon
