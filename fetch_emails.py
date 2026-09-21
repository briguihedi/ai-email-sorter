"""
Étape 1 (v2) : Se connecter à Gmail et récupérer les derniers emails.

Changement : SCOPES passe de "readonly" à "modify" pour permettre
l'application de labels (nécessaire pour l'automatisation d'actions).
"""

import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# "modify" permet de lire ET d'appliquer des labels (mais PAS de supprimer
# définitivement des emails - c'est une permission raisonnable et sûre)
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    """Authentifie l'utilisateur et retourne un objet 'service' pour appeler l'API Gmail."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_email_text(msg_payload):
    """Extrait le texte brut d'un email (gère les emails simples et multipart)."""
    if "parts" in msg_payload:
        for part in msg_payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    else:
        data = msg_payload["body"].get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return ""


def fetch_recent_emails(max_results=20):
    """Récupère les X derniers emails avec leur sujet, expéditeur et contenu."""
    service = get_gmail_service()

    results = service.users().messages().list(userId="me", maxResults=max_results).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        full_msg = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()

        headers = full_msg["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(sans sujet)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "(inconnu)")
        body = get_email_text(full_msg["payload"])

        emails.append({
            "id": msg["id"],
            "subject": subject,
            "from": sender,
            "body": body[:500],
        })

    return emails


def get_or_create_label(service, label_name):
    """Trouve l'ID d'un label existant, ou le crée s'il n'existe pas encore."""
    labels = service.users().labels().list(userId="me").execute().get("labels", [])

    for label in labels:
        if label["name"].lower() == label_name.lower():
            return label["id"]

    # Le label n'existe pas encore, on le crée
    new_label = service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        },
    ).execute()

    return new_label["id"]


def apply_label(service, message_id, label_name):
    """Applique un label à un email donné (le crée d'abord si besoin)."""
    label_id = get_or_create_label(service, f"AI-Sorted/{label_name}")

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]},
    ).execute()


if __name__ == "__main__":
    print("Connexion à Gmail...")
    emails = fetch_recent_emails(max_results=10)

    print(f"\n{len(emails)} emails récupérés :\n")
    for i, email in enumerate(emails, 1):
        print(f"--- Email {i} ---")
        print(f"De : {email['from']}")
        print(f"Sujet : {email['subject']}")
        print(f"Contenu (extrait) : {email['body'][:100]}...")
        print()