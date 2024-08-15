import spacy
import pandas as pd
from langdetect import detect
from transformers import T5ForConditionalGeneration, T5Tokenizer
from mtranslate import translate
import time

# Charger le modèle de paraphrase
model_path = './PEFT_2/PEFT_v2/checkpoint-10000'
model = T5ForConditionalGeneration.from_pretrained(model_path)
tokenizer = T5Tokenizer.from_pretrained('./PEFT_2/PEFT_v2')

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

# Fonction de paraphrase avec gestion de texte long
def paraphraser(text, model, tokenizer):
    input_text = f"paraphrase: {text}"
    inputs = tokenizer.encode(
        input_text,
        return_tensors='pt',
        max_length=256,
        padding='max_length',
        truncation=True
    )

    # Générer le texte paraphrasé
    corrected_ids = model.generate(
        inputs,
        max_length=256,
        num_beams=5,
        early_stopping=True
    )

    # Décoder le texte paraphrasé
    paraphrase = tokenizer.decode(
        corrected_ids[0],
        skip_special_tokens=True
    )
    return paraphrase

# Fonction de traduction avec gestion des tentatives de nouvelle connexion
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

# Fonction pour traiter le texte
def process_text(text, model, tokenizer):
    lang = detect(text)
    if lang != 'en':
        text_en = traduire(text, lang, 'en')
    else:
        text_en = text

    paraphrased_text_en = paraphraser(text_en, model, tokenizer)
    """
    if lang != 'en':
        paraphrased_text = traduire(paraphrased_text_en, 'en', 'fr')
    else:
        paraphrased_text = paraphrased_text_en
    """
    return paraphrased_text_en

# Fonction principale pour traiter le fichier Excel
def traiter_fichier_excel(input_file, output_file):
    df = pd.read_excel(input_file)
    
    # Remplacer les valeurs NaN par des chaînes vides pour éviter les erreurs
    df['titre_filtre'] = df['titre_filtre'].fillna('')
    df['description_filtre'] = df['description_filtre'].fillna('')
    
    # Paraphraser le titre et la description

    df['titre_en'] = df['titre_filtre'].apply(lambda x: process_text(x, model, tokenizer))
    df['description_en'] = df['description_filtre'].apply(lambda x: process_text(x, model, tokenizer))
    df['titre_fr'] = df['titre_en'].apply(lambda x: traduire(x, "en", "fr", max_length=500))
    df['description_fr'] = df['description_en'].apply(lambda x: traduire(x, "en", "fr", max_length=500))
    df['titre_arb'] = df['titre_en'].apply(lambda x: traduire(x, "en", "ar", max_length=500))
    df['description_arb'] = df['description_en'].apply(lambda x: traduire(x, "en", "ar", max_length=500))
    
    # Créer un nouveau dataframe avec les colonnes nécessaires
    new_df = df[['titre_fr','description_fr','titre_en','description_en','titre_arb', 'description_arb', 'date', 'tag', 'source_link']]
    
    # Sauvegarder le nouveau dataframe dans un fichier Excel
    new_df.to_excel(output_file, index=False)

# Exemple d'utilisation
# traiter_fichier_excel('input.xlsx', 'output.xlsx')
