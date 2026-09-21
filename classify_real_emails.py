"""
Étape 3 : Appliquer le modèle entraîné sur de VRAIS emails récupérés depuis Gmail.
Ça nous permet de voir l'écart entre performance sur données d'entraînement
et performance sur données réelles.
"""

import pickle
from fetch_emails import fetch_recent_emails

# Charger le modèle et le vectorizer déjà entraînés (créés par train_classifier.py)
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)


def classify_text(text):
    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)[0]
    probabilities = model.predict_proba(text_vec)[0]
    confidence = max(probabilities) * 100
    return prediction, confidence


if __name__ == "__main__":
    print("Récupération de tes vrais emails Gmail...")
    emails = fetch_recent_emails(max_results=20)

    if not emails:
        print("\nAucun email trouvé dans ta boîte. Envoie-toi quelques emails de test "
              "(factures, questions, pub...) puis relance ce script.")
    else:
        print(f"\n{len(emails)} emails réels trouvés. Classification en cours...\n")

        for i, email in enumerate(emails, 1):
            # On combine le sujet + le début du corps pour la classification
            combined_text = f"{email['subject']} {email['body']}"
            category, confidence = classify_text(combined_text)

            print(f"--- Email {i} ---")
            print(f"De : {email['from']}")
            print(f"Sujet : {email['subject']}")
            print(f"→ Catégorie prédite : {category} (confiance : {confidence:.1f}%)")
            print()
