"""
Étape 3 (v3 - nouvelle librairie google-genai) : Classer des emails avec Gemini.

Note : Google a remplacé l'ancienne librairie "google.generativeai" par
"google-genai". On utilise donc "from google import genai" maintenant.
"""

import os
import json
from dotenv import load_dotenv
from google import genai
from fetch_emails import fetch_recent_emails

# Charge la clé API depuis le fichier .env (jamais écrite en dur dans le code)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.5-flash-lite"  # rapide et le moins cher de la gamme actuelle

CATEGORIES = ["Facture", "Support", "RH", "Spam", "Commercial", "Newsletter/Notification", "Autre"]


def classify_email(subject, body):
    """Envoie l'email à Gemini et lui demande de choisir une catégorie."""

    prompt = f"""Tu es un assistant qui classe des emails dans des catégories précises.

Catégories possibles : {", ".join(CATEGORIES)}

- Facture : documents de facturation, paiements, relances de paiement
- Support : demandes d'aide technique, bugs, problèmes de connexion
- RH : congés, contrats, paie, recrutement, formation interne
- Spam : publicité douteuse, phishing, arnaques
- Commercial : propositions commerciales, devis, offres produits
- Newsletter/Notification : newsletters, notifications automatiques de comptes (sécurité, mises à jour, confirmations de connexion)
- Autre : si aucune catégorie ne correspond clairement

Email à classer :
Sujet : {subject}
Contenu : {body[:500]}

Réponds UNIQUEMENT au format JSON suivant, sans texte avant ou après, sans balises markdown :
{{"category": "NOM_DE_LA_CATEGORIE", "confidence": NOMBRE_ENTRE_0_ET_100, "reason": "explication en une courte phrase"}}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    text = response.text.strip()

    # Nettoie la réponse au cas où Gemini ajoute des balises markdown ```json
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(text)
        return result
    except json.JSONDecodeError:
        return {"category": "Erreur", "confidence": 0, "reason": f"Réponse non parsable : {text}"}


if __name__ == "__main__":
    print("Récupération de tes vrais emails Gmail...")
    emails = fetch_recent_emails(max_results=10)

    if not emails:
        print("\nAucun email trouvé dans ta boîte.")
    else:
        print(f"\n{len(emails)} emails trouvés. Classification avec Gemini en cours...\n")

        for i, email in enumerate(emails, 1):
            result = classify_email(email["subject"], email["body"])

            print(f"--- Email {i} ---")
            print(f"De : {email['from']}")
            print(f"Sujet : {email['subject']}")
            print(f"-> Catégorie : {result.get('category')} (confiance : {result.get('confidence')}%)")
            print(f"  Raison : {result.get('reason')}")
            print()