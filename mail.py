import imaplib
import email
import time
import json
from email.header import decode_header

with open('data.json', 'r') as f:
    data = json.load(f)

IMAP_HOST = "mail.kaasijs.com"
IMAP_PORT = 993

BRIDGE_USERNAME = data["user"]["email"]
BRIDGE_PASSWORD = data["user"]["password"]


def decode_text(value):
    if not value:
        return ""

    result = []

    for text, encoding in decode_header(value):
        if isinstance(text, bytes):
            result.append(
                text.decode(
                    encoding or "utf-8",
                    errors="replace"
                )
            )
        else:
            result.append(text)

    return "".join(result)


def get_email_body(msg):
    if msg.is_multipart():

        html_body = None

        for part in msg.walk():

            content_type = part.get_content_type()
            disposition = str(
                part.get("Content-Disposition", "")
            )

            if "attachment" in disposition:
                continue

            payload = part.get_payload(decode=True)

            if not payload:
                continue

            charset = (
                part.get_content_charset()
                or "utf-8"
            )

            body = payload.decode(
                charset,
                errors="replace"
            )

            if content_type == "text/plain":
                return body

            if content_type == "text/html":
                html_body = body

        return html_body or ""

    payload = msg.get_payload(decode=True)

    if payload:
        return payload.decode(
            msg.get_content_charset() or "utf-8",
            errors="replace"
        )

    return ""


def wait_for_email(
    sender=None,
    subject=None,
    timeout=300,
    check_every=5
):

    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)

    mail.login(
        BRIDGE_USERNAME,
        BRIDGE_PASSWORD
    )
    print("loggedin")

    mail.select("INBOX")

    start_time = time.time()

    try:

        while time.time() - start_time < timeout:

            status, data = mail.search(
                None,
                "UNSEEN"
            )

            if status == "OK":

                message_ids = data[0].split()

                for message_id in reversed(message_ids):

                    status, message_data = mail.fetch(
                        message_id,
                        "(RFC822)"
                    )

                    if status != "OK":
                        continue

                    raw_email = message_data[0][1]

                    msg = email.message_from_bytes(
                        raw_email
                    )

                    from_address = decode_text(
                        msg.get("From")
                    )

                    email_subject = decode_text(
                        msg.get("Subject")
                    )

                    if sender:
                        if sender.lower() not in from_address.lower():
                            continue

                    if subject:
                        if subject.lower() not in email_subject.lower():
                            continue

                    return {
                        "from": from_address,
                        "subject": email_subject,
                        "date": msg.get("Date"),
                        "body": get_email_body(msg),
                        "raw": raw_email,
                    }

            time.sleep(check_every)

    finally:
        mail.logout()

    raise TimeoutError(
        f"No matching email received within {timeout} seconds."
    )