"""
Étape 4 (v2) : Script final - Automation complète avec rapport visuel.
Récupère les emails -> les classe avec Gemini -> applique un label Gmail
-> génère un rapport HTML stylé au lieu d'un simple affichage terminal.
"""

import os
import json
from dotenv import load_dotenv
from google import genai
from fetch_emails import fetch_recent_emails, get_gmail_service, apply_label
from report_generator import generate_html_report

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.5-flash-lite"

CATEGORIES = ["Facture", "Support", "RH", "Spam", "Commercial", "Newsletter-Notification", "Autre"]


def classify_email(subject, body):
    prompt = f"""Tu es un assistant qui classe des emails dans des catégories précises.

Catégories possibles : {", ".join(CATEGORIES)}

- Facture : documents de facturation, paiements, relances de paiement
- Support : demandes d'aide technique, bugs, problèmes de connexion
- RH : congés, contrats, paie, recrutement, formation interne
- Spam : publicité douteuse, phishing, arnaques
- Commercial : propositions commerciales, devis, offres produits
- Newsletter-Notification : newsletters, notifications automatiques de comptes
- Autre : si aucune catégorie ne correspond clairement

Email à classer :
Sujet : {subject}
Contenu : {body[:500]}

Réponds UNIQUEMENT au format JSON suivant, sans texte avant ou après, sans balises markdown :
{{"category": "NOM_DE_LA_CATEGORIE", "confidence": NOMBRE_ENTRE_0_ET_100, "reason": "explication en une courte phrase"}}
"""

    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    text = response.text.strip().replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"category": "Autre", "confidence": 0, "reason": f"Réponse non parsable : {text}"}


if __name__ == "__main__":
    print("Connexion à Gmail...")
    service = get_gmail_service()

    print("Récupération des emails...")
    emails = fetch_recent_emails(max_results=10)

    if not emails:
        print("\nAucun email trouvé.")
    else:
        print(f"\n{len(emails)} emails trouvés. Classification + application des labels...\n")

        results = []
        for i, email in enumerate(emails, 1):
            result = classify_email(email["subject"], email["body"])
            category = result.get("category", "Autre")

            apply_label(service, email["id"], category)

            print(f"Email {i}/{len(emails)} classé : {category}")

            results.append({
                "subject": email["subject"],
                "from": email["from"],
                "category": category,
                "confidence": result.get("confidence", 0),
                "reason": result.get("reason", ""),
            })

        generate_html_report(results)