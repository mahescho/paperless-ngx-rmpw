#!/usr/bin/env python3

import os
import pikepdf


def is_pdf(file_path: str) -> bool:
    return os.path.splitext(file_path.lower())[1] == ".pdf"


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
    print(f"Reading document passwords into memory from {pass_file_path}")
    with open(pass_file_path, "r") as f:
        passwords = f.readlines()

    for p in passwords:
        password = p.strip()
        try:
            with pikepdf.open(
                file_path, password=password, allow_overwriting_input=True
            ) as pdf:
                print(f"Document {file_path} was decrypted succesfully")
                pdf.save(file_path, deterministic_id=True)
                break
        except pikepdf.PasswordError:
            print(f"No password from file {pass_file_path} is working for file {file_path}")
            continue

    if password is None:
        print(f"Password file {pass_file_path} is empty")


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
                        print(f"Attachment {trg_file_path} saved")
                except Exception as e:
                    print(f"Error while writing attachment {trg_file_path}: {e}")
                    continue
            else:
                print(f"Attachment {trg_filename} skipped, because it is not a PDF file")

src_file_path = os.environ.get('DOCUMENT_WORKING_PATH')
pass_file_path = "/usr/src/paperless/scripts/passwords.txt"
consume_path = "/usr/src/paperless/consume/"

# Script execution
task_id = os.environ.get('TASK_ID')
print(f"Kicking off pre-consumption script for task {task_id}")

if src_file_path is None:
    print("No file path available in environment variable 'DOCUMENT_WORKING_PATH'")
    exit(0)

if not is_pdf(src_file_path):
    print(f"File {src_file_path} not a PDF file")
    exit(0)

if is_pdf_encrypted(src_file_path):
    print(f"Document {src_file_path} is encrypted. Proceeding with decryption")
    unlock_pdf(src_file_path)
else:
    print(f"Document {src_file_path} is not encrypted. Proceeding without decryption")

if pdf_has_attachments(src_file_path):
    print(f"Document {src_file_path} contains attachments. Proceeding with extracting the attachments")
    extract_pdf_attachments(src_file_path)
else:
    print(f"Document {src_file_path} has no attachments. Proceeding without decryption")
