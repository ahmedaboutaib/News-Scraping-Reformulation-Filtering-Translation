from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation
from selenium.common.exceptions import NoSuchElementException



def get_titles_urls(driver,date):

    article_urls = []

    try:
        # Récupérer la page web pour la catégorie donnée
        driver.get("https://www.lepoint.fr/tags/maroc")
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#content > div:nth-child(2) > section.articles")))

        # Récupérer les éléments de la liste d'articles
        articles = driver.find_elements(By.CSS_SELECTOR, "#content > div:nth-child(2) > section.articles > article")
        for article in articles:
            try:
                url = article.find_element(By.CSS_SELECTOR, "div:nth-child(2) > a").get_attribute("href")
                if date in url :
                 article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles : {e}")

    return article_urls


def get_article_info(url, driver, date):

    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        article=WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#content > article")))
        # Récupérer les éléments nécessaires
        #article = driver.find_element(By.CSS_SELECTOR, "#content > article")
    
        title = ""
        tag = ""
        description1 = ""
        description2 = ""
        
        # Essayer de trouver chaque élément et assigner les valeurs
        try:
            title = article.find_element(By.CSS_SELECTOR, "#haut > h1").text.strip().replace(""," ")
        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")
        
        # Récupérer les descriptions
        try:
           description2 = " ".join([p.text.strip() for p in article.find_elements(By.CSS_SELECTOR, "#contenu > p")]).replace(""," ")
        except NoSuchElementException as e:
            # Si l'élément description1 n'est pas trouvé, laisser la description1 vide
            print("L'élément 'description2' n'a pas été trouvé.")
        
        try:
            description1_element = article.find_element(By.CSS_SELECTOR, "#haut > p.chapo")
            description1 = description1_element.text.strip().replace(""," ")
        except NoSuchElementException as e:
            # Si l'élément description2 n'est pas trouvé, laisser la description2 vide
            print("L'élément 'description1' n'a pas été trouvé.")
        
        # Concaténer les descriptions si elles ne sont pas vides
        if description1 and description2:
            article_info = {
                "titre": title,
                "description": f"{description1} {description2}",
                "date": date,
                "tag": tag,
                "source_link": "https://www.lepoint.fr/tags/maroc"
            }
        elif description1:
            article_info = {
                "titre": title,
                "description": description1,
                "date": date,
                "tag": tag,
                "source_link": "https://www.lepoint.fr/tags/maroc"
            }
        elif description2:
            article_info = {
                "titre": title,
                "description": description2,
                "date": date,
                "tag": tag,
                "source_link": "https://www.lepoint.fr/tags/maroc"
            }
        else:
            article_info = {
                "titre": title,
                "description": "",
                "date": date,
                "tag": tag,
                "source_link": "https://www.lepoint.fr/tags/maroc"
            }
        
        return article_info

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None
    


def main11(date,driver):
   

     
    try:


        # Récupérer la page web principale
        article_urls  = get_titles_urls(driver,date)


        
        
        news_list = []

        for url in tqdm(article_urls, desc = f"Progression dans https://www.lepoint.fr/tags/maroc à la date {date}"):
            article_info = get_article_info(url, driver, date)
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
        print(f"Une erreur s'est produite lors de la récupération https://www.lepoint.fr/tags/maroc  ' : {e}")
