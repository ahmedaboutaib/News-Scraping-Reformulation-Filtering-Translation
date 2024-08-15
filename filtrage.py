
import spacy
import pandas as pd
from langdetect import detect
from mtranslate import translate
import time




# Dictionnaire pour les modèles SpaCy
spacy_models = {
    'fr': 'fr_core_news_sm',
    'en': 'en_core_web_sm',
    'ar': 'xx_ent_wiki_sm'  # Utilisation du modèle multi-langue pour l'arabe
}

# Fonction pour charger le modèle SpaCy avec le sentencizer
def load_spacy_model(lang_code):
    model_name = spacy_models.get(lang_code, 'xx_ent_wiki_sm')
    nlp = spacy.load(model_name)
    if 'parser' not in nlp.pipe_names and 'sentencizer' not in nlp.pipe_names:
        sentencizer = nlp.add_pipe('sentencizer')
    return nlp





def traduire(text, from_lang, to_lang, max_length=500, retries=3, delay=5):
    nlp = load_spacy_model(from_lang)
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    translations = []

    current_segment = ""
    for sentence in sentences:
        if len(current_segment) + len(sentence) + 1 > max_length:
            success = False
            for _ in range(retries):
                try:
                    translations.append(translate(current_segment, to_lang, from_lang))
                    success = True
                    break
                except Exception as e:
                    print(f"Erreur de traduction: {e}. Nouvelle tentative dans {delay} secondes.")
                    time.sleep(delay)
            if not success:
                raise Exception("La traduction a échoué après plusieurs tentatives.")
            current_segment = sentence
        else:
            if current_segment:
                current_segment += " " + sentence
            else:
                current_segment = sentence

    if current_segment:
        success = False
        for _ in range(retries):
            try:
                translations.append(translate(current_segment, to_lang, from_lang))
                success = True
                break
            except Exception as e:
                print(f"Erreur de traduction: {e}. Nouvelle tentative dans {delay} secondes.")
                time.sleep(delay)
        if not success:
            raise Exception("La traduction a échoué après plusieurs tentatives.")

    return ' '.join(translations)


def traduction_fr(text):
    if not text.strip():  # Vérifier si le texte est vide
        return text  # Retourner le texte original si vide

    try:
        lang = detect(text)
    except Exception as e:
        print(f"Erreur lors de la détection de la langue : {e}")
        return text  # Retourner le texte original en cas d'erreur

    if lang != 'fr':
        try:
            text_fr = traduire(text, lang, 'fr')
        except Exception as e:
            print(f"Erreur lors de la traduction : {e}")
            text_fr = text  # Retourner le texte original en cas d'erreur de traduction
    else:
        text_fr = text

    return text_fr


# Fonction pour vérifier si au moins un mot est présent dans une cellule
def contains_any_word(cell, mots):
    for mot in mots:
        if mot.lower() in str(cell).lower():
            return True
    return False


def lire_fichier(fichier):
    with open(fichier, 'r', encoding='utf-8') as f:
        lignes = f.readlines()
        # Enlever les sauts de ligne à la fin de chaque ligne
        lignes_propres = [ligne.strip() for ligne in lignes]
    return lignes_propres






def filtre( nom_fichier_excel) : 

    df = pd.read_excel(nom_fichier_excel)

    # Remplacer les valeurs NaN par des chaînes vides pour éviter les erreurs
    df['titre'] = df['titre'].fillna('')
    df['description'] = df['description'].fillna('')

    # Paraphraser le titre et la description

    df['titre_filtre'] = df['titre'].apply(lambda x: traduction_fr(x))
    df['description_filtre'] = df['description'].apply(lambda x: traduction_fr(x))
    new_df = df[['titre_filtre','description_filtre','date', 'tag', 'source_link']]



    # Liste de mots à rechercher
    nom_fichier = 'keyword.txt'
    mots_a_rechercher = lire_fichier(nom_fichier)
    print(mots_a_rechercher)



    # Créer un masque booléen pour les lignes contenant au moins un des mots dans n'importe quelle colonne
    masque = new_df.apply(lambda row: contains_any_word(row, mots_a_rechercher), axis=1)

    # Garder les lignes qui satisfont au moins une condition
    nouveau_df = new_df[masque]

    # Enregistrer les lignes filtrées dans un nouveau fichier Excel
    nom_fichier_sortie = f'filtre-{nom_fichier_excel}'
    nouveau_df.to_excel(nom_fichier_sortie, index=False)
    print('fin ------------------------------------------')

    
