from mail import wait_for_email

print("Waiting for email...")

email = wait_for_email(
    sender="no-reply@thuisbezorgd.nl",
    subject="Your verification code",
    timeout=300,
)

print("\nEmail received!")
print("----------------")
print("From:", email["from"])
print("Subject:", email["subject"])
print("Date:", email["date"])
print("\nBody:")
print(email["body"])

import re
from bs4 import BeautifulSoup

def extract_verification_code(html):
    soup = BeautifulSoup(html, "html.parser")

    # Find the text inside the email's code box
    for td in soup.find_all("td"):
        text = td.get_text(strip=True)

        if re.fullmatch(r"[A-Z0-9]{6}", text):
            return text

    return None


# Example
code = extract_verification_code(email["body"])

if code:
    print("Verification code:", code)