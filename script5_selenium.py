from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation
from function_basics import change_date_maj  # Fonction pour changer le format de la date


def get_titles_urls(driver, date_format):
    """
    Cette fonction récupère les URLs des articles sur la page principale du site Web.
    
    Args:
        driver: WebDriver pour le navigateur
        date_format: Format de la date pour la recherche des articles
    
    Returns:
        Une liste des URLs des articles
    """
    article_urls = []

    try:
        # Récupérer la page web pour la catégorie donnée
        driver.get("https://www.lemonde.fr/maroc/")
        # Attendre que les éléments se chargent
        articles = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#river > div > div > section > a")))
        
        # Récupérer les URLs des articles
        for article in articles:
            try:
                url = article.get_attribute("href")
                if date_format in url :
                     article_urls.append(url)

            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")

        
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles : {e}")
    
    return article_urls


def get_article_info(url, driver, date_format):
    """
    Cette fonction récupère les informations d'un article spécifique.
    
    Args:
        url: URL de l'article
        driver: WebDriver pour le navigateur
        date_format: Format de la date pour l'article
    
    Returns:
        Un dictionnaire contenant les informations de l'article
    """
    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#habillagepub > section")))
        # Récupérer les éléments nécessaires
        article = driver.find_element(By.CSS_SELECTOR, "#habillagepub > section")
        
    
        title = ""
        date = ""
        tag = ""
        description1 = ""
        #description2 = ""


        # Essayer de trouver chaque élément et assigner les valeurs

      
        try:
            title = article.find_element(By.CSS_SELECTOR, "header > div > div > h1").text.strip()

        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")
    
        try:
            description2 = " ".join([p.text.strip() for p in driver.find_elements(By.CSS_SELECTOR, "#habillagepub > section > section > article > p")])
            #article.find_element(By.CSS_SELECTOR, "section > article").text.strip()
            print(f"eeeeeeeeeeeeeeeeeeee{description2}")
       
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")
            
        try:
            description1 = article.find_element(By.CSS_SELECTOR, "header > div > div > p").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")

        article_info = {
            "titre": title,
            "description": f"{description1} {description2}",
            "date": date_format,
            "tag" : tag,
            "source_link": "https://www.lemonde.fr/maroc/"
        }
            
        return article_info
       
      
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None
    

def main5(date,driver):
    """
    Fonction principale pour exécuter le scraping des articles du site Web.
    
    Args:
        date: Date pour laquelle les articles doivent être récupérés
    
    """

    
    try:
        elements = date.split("-")
        date_format = f"{elements[2]}/{elements[1]}/{elements[0]}"
        print(date_format)

        # Récupérer les URLs des articles sur la page principale
        article_urls  = get_titles_urls(driver, date_format)
   
        
        news_list = []

        # Parcourir les URLs des articles et récupérer les informations
        for url in tqdm(article_urls, desc=f"Scraping des articles sur https://www.lemonde.fr/maroc/ à la date {date} "):
            article_info = get_article_info(url, driver, date_format)
            if article_info is not None:
                news_list.append(article_info)
                
        # Vérifier si le fichier Excel existe déjà
        if os.path.isfile(f'{date}.xlsx'):
            # Charger le fichier Excel existant dans un DataFrame
            existing_df = pd.read_excel(f'{date}.xlsx')
            # Vérifier si la liste de nouvelles n'est pas vide
            if not news_list:
                print("La liste de nouvelles est vide. Aucune donnée n'a été ajoutée.")
            else:
                # Créer un DataFrame à partir de la liste de nouvelles
                new_df = pd.DataFrame(news_list)
                # Concaténer le DataFrame existant avec le nouveau DataFrame
                df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            # Si le fichier n'existe pas, créer un DataFrame à partir de la liste de nouvelles
            df = pd.DataFrame(news_list)

        # Vérifier si le DataFrame contient des données
        if 'df' in locals():
            if not df.empty:
                df = df[['titre', 'description', 'date', 'tag', 'source_link']]
                df.to_excel(f'{date}.xlsx', index=False)
                print(f"Les données ont été exportées avec succès vers '{date}.xlsx'.")
            else:
                print("Le DataFrame est vide. Aucun fichier Excel n'a été créé.")
        else:
            print("La liste de nouvelles est vide. Aucune donnée n'a été ajoutée.")
        
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération https://www.lemonde.fr/maroc/  : {e}")

