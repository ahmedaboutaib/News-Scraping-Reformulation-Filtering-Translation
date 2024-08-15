from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation
from selenium.common.exceptions import NoSuchElementException

def get_titles_urls(url,driver,date_format, i):
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
        # Récupérer la page web pour la date spécifiée
        driver.get(url)
        # Attendre que les éléments se chargent
        articles = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#tq > div.wrapper > main > section:nth-child(2) > div > div.col-large.col-gutter > ul > li > div > div.article-content > h3 > a")))

        # Récupérer les URLs des articles
        for article in articles:
            try:
                url = article.get_attribute("href")
                article_urls.append(url)

            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")

        if i != 10:
            try:
                page_url = f"https://telquel.ma/{date_format}/page/{i+2}"
                return article_urls + get_titles_urls(page_url, driver,date_format,i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvé, return article_urls
                print("'la page suivante' n'a pas été trouvé.")
                return article_urls
        else:
            return article_urls


    except Exception as e:
        print(f"la page https://telquel.ma/{date_format}/page/{i+1} est vide.")


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
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tq > div.wrapper > main > div > main")))
        # Récupérer les éléments nécessaires
        article = driver.find_element(By.CSS_SELECTOR, "#tq > div.wrapper > main > div > main")

        title = ""
        tag = ""
        description2 = ""
        description1 = ""

        try:
            title = article.find_element(By.CSS_SELECTOR, "header > div > h2").text.strip().replace(""," ")

        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")
            
        try:
            tag_element = article.find_element(By.CSS_SELECTOR, "section > div > div.col-large.col-gutter > ul")
            tag = tag_element.text.strip().replace(""," ")
        except NoSuchElementException as e:
            # Si l'élément tag n'est pas trouvé, laisser tag vide
            print("L'élément 'tag' n'a pas été trouvé.")
        
        # Récupérer les descriptions
        try:
            description2 = " ".join([p.text.strip() for p in article.find_elements(By.CSS_SELECTOR, "section > div > div.col-large.col-gutter p")]).replace(""," ")

        except NoSuchElementException as e:
            # Si l'élément description1 n'est pas trouvé, laisser la description1 vide
            print("L'élément 'description1' n'a pas été trouvé.")
        
        try:
            description1_element = article.find_element(By.CSS_SELECTOR, "section > div > div.col-large.col-gutter h2")
            description1 = description1_element.text.strip().replace(""," ")
        except NoSuchElementException as e:
            # Si l'élément description2 n'est pas trouvé, laisser la description2 vide
            print("L'élément 'description2' n'a pas été trouvé.")
        
        # Concaténer les descriptions si elles ne sont pas vides
        if description1 and description2:
            article_info = {
                "titre": title,
                "description": f"{description1} {description2}",
                "date": date_format,
                "tag": tag,
                "source_link": "https://telquel.ma/"
            }
        elif description1:
            article_info = {
                "titre": title,
                "description": description1,
                "date": date_format,
                "tag": tag,
                "source_link": "https://telquel.ma/"
            }
        elif description2:
            article_info = {
                "titre": title,
                "description": description2,
                "date": date_format,
                "tag": tag,
                "source_link": "https://telquel.ma/"
            }
        else:
            article_info = {
                "titre": title,
                "description": "",
                "date": date_format,
                "tag": tag,
                "source_link": "https://telquel.ma/"
            }

        return article_info

    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None


def main8(date,driver):
    """
    Fonction principale pour exécuter le scraping des articles du site Web.

    Args:
        date: Date pour laquelle les articles doivent être récupérés

    """


    try:
        # Formatter la date dans le format attendu par le site Web
        elements = date.split("-")
        date_format = f"{elements[2]}/{elements[1]}/{elements[0]}"
        url_titles = f"https://telquel.ma/{date_format}"
        # Récupérer les URLs des articles sur la page principale
        article_urls = get_titles_urls(url_titles,driver,date_format,0)

        news_list = []

        # Parcourir les URLs des articles et récupérer les informations
        for url in tqdm(article_urls, desc=f"Scraping des articles sur https://telquel.ma/ à la date {date} "):
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
        print(f"Une erreur s'est produite lors de la récupération https://telquel.ma/' : {e}")

