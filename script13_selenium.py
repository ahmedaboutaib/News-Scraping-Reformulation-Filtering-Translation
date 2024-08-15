from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation



def get_titles_urls(driver, date_format):

    article_urls = []

    try:
        # Récupérer la page web pour la catégorie donnée
        driver.get("https://www.finances.gov.ma/fr/Pages/actualites.aspx")
   
        

        
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#ctl00_ctl38_g_11c99868_a4bd_4f4b_864e_fc7f0100ba7e > div.container > div > div.content.pagination1")))

        # Récupérer les éléments de la liste d'articles
        articles = driver.find_elements(By.CSS_SELECTOR, "#ctl00_ctl38_g_11c99868_a4bd_4f4b_864e_fc7f0100ba7e > div.container > div > div.content.pagination1 > div")

        for i in range(min(40, len(articles))):
            try:
                url = articles[i].find_element(By.CSS_SELECTOR, "div.col-md-7 > h2 > a").get_attribute("href")
                date = articles[i].find_element(By.CSS_SELECTOR, "div.col-md-7 > p:nth-child(2)").text.strip()
                if date_format in date:
                    article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")
        
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles : {e}")
    
    return article_urls


def get_article_info(url, driver, date_format):

    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#ctl00_ctl38_g_4003d338_917a_4218_9c89_0f8e468249a7")))
        # Récupérer les éléments nécessaires
        article = driver.find_element(By.CSS_SELECTOR, "#ctl00_ctl38_g_4003d338_917a_4218_9c89_0f8e468249a7")
    
        title = ""
        date = ""
        tag = ""
        description1 = ""
        description2 = ""

 
        # Essayer de trouver chaque élément et assigner les valeurs
        try:
            title = article.find_element(By.CSS_SELECTOR, "div > div > div > h4").text.strip()

        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")
    
        try:
            description2 = article.find_element(By.CSS_SELECTOR, "div > div > div > div.ExternalClassF190663F347F4BAE8E285F8EAA640B69").text.strip()
            print(description2)
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")
            
        try:
            description1 = article.find_element(By.CSS_SELECTOR, "div > div > div > p.post-chapeau").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")

        article_info = {
            "titre": title,
            "description": description1,
            "date": date_format,
            "tag" : tag,
            "source_link": "https://www.finances.gov.ma/fr/Pages/actualites.aspx"
        }
            
        return article_info

        
        
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None
    


def main13(date,driver):
   

     
    try:
        date_format = "/".join(date.split("-"))
        print(date_format)

        #Récupérer la page web principale
        article_urls  = get_titles_urls(driver, date_format)

        news_list = []

        for url in tqdm(article_urls, desc=f"Scraping des articles sur https://www.finances.gov.ma/fr/Pages/actualites.aspx à la date {date} "):
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
        print(f"Une erreur s'est produite lors de la récupération  https://www.finances.gov.ma/fr/Pages/actualites.aspx ' : {e}")

