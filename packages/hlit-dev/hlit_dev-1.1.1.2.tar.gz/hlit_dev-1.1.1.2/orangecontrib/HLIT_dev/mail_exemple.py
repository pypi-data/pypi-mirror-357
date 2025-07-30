import imaplib
import smtplib
import email
from email.header import decode_header
import time
from Orange.widgets.orangecontrib.AAIT.utils import MetManagement
import os
from email import policy
from email.message import EmailMessage

AGENT = "agent.ia"
MY_DOMAIN = "@institut-ia.com"
EMAIL = AGENT + MY_DOMAIN
PASSWORD = "jfoi xbud rata aysp"
INTERVAL_SECONDS = 1  # nombre de secondes entre chaque vérification

def clean_addresses(field):
    """Retourne une liste d'adresses nettoyées sans ton adresse"""
    if not field:
        return []
    addresses = email.utils.getaddresses([field])
    return [addr for name, addr in addresses if addr.lower() != EMAIL.lower()]

def write_mail_in_folder(agent_name, folder_type="in"):
    if agent_name is None or agent_name == "":
        print("agent_name doit etre renseigné")
        return None
    chemin_dossier= MetManagement.get_path_mailFolder()
    if not os.path.exists(chemin_dossier):
        os.makedirs(chemin_dossier)
    real_time = MetManagement.get_second_from_1970()
    folder = chemin_dossier + "/" + str(agent_name) + "/" + str(folder_type) + "/" + str(real_time)
    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        time.sleep(1.5)
        write_mail_in_folder(agent_name, folder_type)
    return folder

def check_new_emails():
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(EMAIL, PASSWORD)
        imap.select("inbox")

        status, messages = imap.search(None, 'UNSEEN')
        mail_ids = messages[0].split()

        if not mail_ids:
            print("Aucun nouveau mail.")
        else:
            for mail_id in mail_ids:
                output_lines = []
                _, msg_data = imap.fetch(mail_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        from email.parser import BytesParser

                        # Utilise :
                        msg = BytesParser(policy=policy.default).parsebytes(response_part[1])

                        # Sujet
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")

                        # Expéditeur
                        from_ = msg.get("From")

                        # Destinataires
                        to_emails = clean_addresses(msg.get("To", ""))
                        cc_emails = clean_addresses(msg.get("Cc", ""))

                        # Corps
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    payload = part.get_payload(decode=True)
                                    charset = part.get_content_charset()
                                    body = payload.decode(charset if charset else "utf-8", errors="replace")
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode(errors="replace")

                        # Format de sortie
                        output_lines.append(f"#$who : {EMAIL}")
                        output_lines.append(f"#$eme : {from_}")
                        output_lines.append(f"#$des : {', '.join(to_emails)}")
                        output_lines.append(f"#$cop : {', '.join(cc_emails)}")
                        output_lines.append(f"#$pri : Normale")
                        output_lines.append(f"#$tit : {subject}")
                        output_lines.append(f"#$txt : {body.strip()}")
                        output_lines.append("")

                        if output_lines != []:
                            folder = write_mail_in_folder(AGENT, "in")
                            if folder is None:
                                print("erreur dans le folder de mail")
                                return

                            with open(folder + "/" + "mail.txt", "w", encoding="utf-8") as f:
                                f.write("\n".join(output_lines))
                                f.close()

                            with open(folder + "/" + "mail.ok", "w") as f:
                                f.close()

                            for part in msg.iter_attachments():
                                filename = part.get_filename()
                                if filename:
                                    folder_pj = folder + "/" + "pj"
                                    if not os.path.exists(folder_pj):
                                        os.makedirs(folder_pj)
                                    filepath = os.path.join(folder_pj, filename)
                                    with open(filepath, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    f.close()

        imap.logout()
    except Exception as e:
        print(f"Erreur lors de la vérification des mails : {e}")



def send_mail(expediteur, mot_de_passe, destinataire, sujet, contenu,piece_jointe_path=None, serveur="smtp.gmail.com", port=587):
    msg = EmailMessage()
    msg['From'] = expediteur
    msg['To'] = destinataire
    msg['Subject'] = sujet
    msg.set_content(contenu)
    # Ajout d'une pièce jointe si fournie
    if piece_jointe_path:
        with open(piece_jointe_path, 'rb') as f:
            data = f.read()
            nom_fichier = piece_jointe_path.split('/')[-1]
            msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=nom_fichier)
    try:
        with smtplib.SMTP(serveur, port) as smtp:
            smtp.starttls()
            smtp.login(expediteur, mot_de_passe)
            smtp.send_message(msg)
    except Exception as e:
        print("❌ Une erreur s'est produite :", e)

if __name__ == "__main__":
    print(f"Surveillance des mails toutes les {INTERVAL_SECONDS} secondes. Ctrl+C pour arrêter.")
    send_mail(
        expediteur=EMAIL,
        mot_de_passe=PASSWORD,
        destinataire="maxime.boix@institut-ia.com",
        sujet="Test depuis Python",
        contenu="Bonjour,\nVoici un test d'envoi de mail avec Python.",
        piece_jointe_path=r"C:\Users\max83\Desktop\Orange_4All_AAIT\Orange_4All_AAIT\Orange\Lib\site-packages\Orange\widgets\orangecontrib\HLIT_dev\widgets\icons\input_interface.png"  # ou "chemin/vers/fichier.pdf"
    )
