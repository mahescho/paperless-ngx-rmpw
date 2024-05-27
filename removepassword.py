#!/usr/bin/env python

import os
import pikepdf


def is_pdf(file_path: str) -> bool:
    return os.path.splitext(file_path)[1] == ".pdf"


def is_pdf_encrypted(file_path: str) -> bool:
    try:
        with pikepdf.open(file_path) as pdf:
            return pdf.is_encrypted
    except:
        return True


def pdf_has_attachments(file_path: str) -> bool:
    try:
        with pikepdf.open(file_path) as pdf:
            return len(pdf.attachments) > 0
    except:
        return False


def unlock_pdf(file_path: str):
    password = None
    print("reading passwords")
    with open(pass_file_path, "r") as f:
        passwords = f.readlines()
    for p in passwords:
        password = p.strip()
        try:
            with pikepdf.open(
                file_path, password=password, allow_overwriting_input=True
            ) as pdf:
                # print("password is working")
                print("unlocked succesfully")
                pdf.save(file_path)
                break
        except pikepdf.PasswordError:
            print("password is not working")
            continue
    if password is None:
        print("empty password file")


def extract_pdf_attachments(file_path: str):
    with pikepdf.open(file_path) as pdf:
        ats = pdf.attachments
        for atm in ats:
            trg_filename = ats.get(atm).filename
            if is_pdf(trg_filename):
                trg_file_path = os.path.join(consume_path, trg_filename)
                try:
                    with open(trg_file_path, "wb") as wb:
                        wb.write(ats.get(atm).obj["/EF"]["/F"].read_bytes())
                        print("saved: ", trg_file_path)
                except:
                    print("error ", trg_file_path)
                    continue
            else:
                print("skipped: ", trg_filename)

src_file_path = os.environ.get('DOCUMENT_WORKING_PATH')
pass_file_path = "/usr/src/paperless/scripts/passwords.txt"
consume_path = "/usr/src/paperless/consume/"

if is_pdf(src_file_path):
    if is_pdf_encrypted(src_file_path):
        print("decrypting pdf")
        unlock_pdf(src_file_path)
    else:
        print("not encrypted")

    if pdf_has_attachments(src_file_path):
        print("getting attachments")
        extract_pdf_attachments(src_file_path)
    else:
        print("no attachments")
else:
    print("not pdf")
