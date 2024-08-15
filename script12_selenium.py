from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation
from function_basics import change_date_maj0  # Fonction pour changer le format de la date
from selenium.common.exceptions import NoSuchElementException

def get_titles_urls(url,driver, date_format,i):
    """
    Récupère les URLs des articles de la page principale.

    :param driver: Instance du WebDriver
    :param date_format: Format de la date à rechercher
    :return: Liste des URLs des articles correspondant à la date
    """
    article_urls = []

    try:
        # Récupérer la page web pour la catégorie des communiqués de presse
        driver.get(url)
        # Attendre que les éléments se chargent
        # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#block-cg-content > div > section > article")))
        articles = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#block-cg-content > div > section > div > article > div.article-format")))

        # Récupérer les éléments de la liste d'articles
        #articles = driver.find_elements(By.CSS_SELECTOR, "#block-cg-content > div > section > div > article > div.article-format")

        for article in articles:
            try:
                url = article.find_element(By.CSS_SELECTOR, "h4.h4  a").get_attribute("href")
                date = article.find_element(By.CSS_SELECTOR, "div > span > span > time").text.strip()
                if date_format in date:
                    article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")
        if i != 5:
            try:
                page = driver.find_element(By.CSS_SELECTOR, "#block-cg-content > div > nav > ul > li.page-item.pager__item--next > a")
                page_url = page.get_attribute("href")
                return article_urls + get_titles_urls(page_url, driver, date_format,i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvé, return article_urls
                print("'la page suivante' n'a pas été trouvé.")
                return article_urls
        else:
            return article_urls       
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles : {e}")

    return article_urls


def get_article_info(url, driver):
    """
    Récupère les informations d'un article spécifique.

    :param url: URL de l'article
    :param driver: Instance du WebDriver
    :return: Dictionnaire contenant les informations de l'article
    """
    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#block-cg-content > article")))
        # Récupérer les éléments nécessaires
        article = driver.find_element(By.CSS_SELECTOR, "#block-cg-content > article")

        title = ""
        date = ""
        tag = ""
        description = ""

        try:
            date = article.find_element(By.CSS_SELECTOR, "div.section-date").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de la date : {e}")

        # Essayer de trouver chaque élément et assigner les valeurs
        try:
            title = article.find_element(By.CSS_SELECTOR, "header > h1 > span").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")

        try:
            description = " ".join([p.text.strip() for p in article.find_elements(By.CSS_SELECTOR, "#read_content > div p")])
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")

        article_info = {
            "titre": title.replace(""," "),
            "description": description.replace(""," "),
            "date": date.replace(""," "),
            "tag": tag.replace(""," "),
            "source_link": "https://www.cg.gov.ma/fr/communiques-de-presse"
        }

        return article_info

    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None


def main12(date,driver):
    """
    Fonction principale pour exécuter le script.

    :param date: Date au format "jj-mm-aaaa"
    """

    try:
        # Convertir la date en format requis pour la recherche
        date_format = change_date_maj0(date).lower()
        print(date_format)
        url ="https://www.cg.gov.ma/fr/communiques-de-presse"
        # Récupérer les URLs des articles
        article_urls = get_titles_urls(url,driver, date_format,0)

        news_list = []

        # Parcourir les URLs des articles et récupérer les informations
        for url in tqdm(article_urls, desc=f"Progression dans https://www.cg.gov.ma/fr/communiques-de-presse à la date {date} "):
            article_info = get_article_info(url, driver)
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
        print(f"Une erreur s'est produite lors de la récupération https://www.cg.gov.ma/fr/communiques-de-presse ' : {e}")
