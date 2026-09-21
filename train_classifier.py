"""
Étape 2 (version corrigée) : Entraîner un modèle IA pour classer des emails par catégorie.

Corrections apportées :
1. stratify=y dans le split : garantit que chaque catégorie est représentée
   proportionnellement dans le train ET le test (avant, une catégorie pouvait
   se retrouver avec 0 exemple de test par hasard).
2. Validation croisée (cross-validation) : au lieu de mesurer la précision sur
   un seul petit split de 10 exemples, on teste sur 5 splits différents et on
   fait la moyenne -> résultat beaucoup plus fiable avec un petit dataset.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
import pickle

# 1. Charger les données d'entraînement
df = pd.read_csv("training_data.csv")
print(f"{len(df)} exemples chargés.")
print(df["category"].value_counts())

X = df["text"]
y = df["category"]

# 2. Vectoriser TOUT le texte (nécessaire avant la validation croisée)
vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

# 3. Validation croisée : découpe les données en 5 groupes, teste 5 fois
#    en changeant à chaque fois quel groupe sert de test -> résultat fiable
model_for_cv = MultinomialNB()
cv_scores = cross_val_score(model_for_cv, X_vec, y, cv=5)
print(f"\nPrécision (validation croisée, 5 essais) : {cv_scores.mean() * 100:.1f}%")
print(f"Détail des 5 essais : {[f'{s*100:.0f}%' for s in cv_scores]}")

# 4. Split classique avec stratify=y pour le rapport détaillé par catégorie
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train_vec = vectorizer.transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = MultinomialNB()
model.fit(X_train_vec, y_train)
y_pred = model.predict(X_test_vec)

print(f"\nPrécision (split unique équilibré) : {accuracy_score(y_test, y_pred) * 100:.1f}%")
print("\nDétail par catégorie :")
print(classification_report(y_test, y_pred, zero_division=0))

# 5. Réentraîner le modèle final sur TOUTES les données (pour un usage réel)
final_model = MultinomialNB()
final_model.fit(X_vec, y)

with open("model.pkl", "wb") as f:
    pickle.dump(final_model, f)
with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("\nModèle final sauvegardé (entraîné sur 100% des données).")


def classify_text(text):
    text_vec = vectorizer.transform([text])
    prediction = final_model.predict(text_vec)[0]
    probabilities = final_model.predict_proba(text_vec)[0]
    confidence = max(probabilities) * 100
    return prediction, confidence


if __name__ == "__main__":
    test_examples = [
        "Bonjour, ma commande n'est jamais arrivée, pouvez-vous vérifier ?",
        "Vous avez été sélectionné pour recevoir 10000 euros, cliquez vite !",
        "Voici votre facture du mois, montant 45.50 euros.",
    ]

    print("\n--- Tests sur de nouveaux exemples ---")
    for text in test_examples:
        category, confidence = classify_text(text)
        print(f"\nTexte : {text[:60]}...")
        print(f"-> Catégorie prédite : {category} (confiance : {confidence:.1f}%)")