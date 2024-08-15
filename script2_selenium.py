from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation
from selenium.common.exceptions import NoSuchElementException

def get_categories_url(menu):
    """
    Cette fonction extrait les URLs des catégories à partir du menu du site Web.

    Args:
        menu: L'élément du menu contenant les catégories.

    Returns:
        list: Une liste des URLs des catégories.
    """
    try:
        categories_url = []

        category_items = menu.find_elements(By.CSS_SELECTOR, "div.main-wrap > a")
        for i in range(0, len(category_items) - 1):
            category = category_items[i].get_attribute("href")
            if category:
                categories_url.append(category)

        return categories_url
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs de catégorie : {e}")
        return []


def get_article_urls(category_url,origin_url, driver,i):
    """
    Cette fonction récupère les URLs des articles d'une catégorie spécifique.

    Args:
        category_url (str): L'URL de la catégorie d'articles.
        driver: Le WebDriver pour le navigateur.

    Returns:
        list: Une liste des URLs d'articles.
    """
    try:
        article_urls = []

        # Récupérer la page web pour la catégorie donnée
        driver.get(category_url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.layout-section div")))
        try:
 
            # Récupérer l'URL du premier article en vedette
            url0 = driver.find_element(By.CSS_SELECTOR, "div:nth-child(2) div div div.container-fluid.double-chain.chain-container > div.row.wrap-bottom > div.col-sm-12.col-md-xl-9.ie-flex-100-percent-sm.column-1.reduce-internal-row-col-gap.chain-col div article h2 a").get_attribute("href")
            article_urls.append(url0)
        except NoSuchElementException as e:
            print("....................")


        # Récupérer les URLs des autres articles
        articles1 = driver.find_elements(By.CSS_SELECTOR, "div:nth-child(2) div div div.ssa-container div div a.link ")
        for article in articles1:
            try:
                url1 = article.get_attribute("href")
                article_urls.append(url1)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")

        articles2 = driver.find_elements(By.CSS_SELECTOR, "section.main div div section.col-sm-12.col-md-12.col-xl-9.col-lg-9.main-padding div div.results-list-container div div div.article-list-text-container div.article-list--headline-container a ")
        for article in articles2:
            try:
                url2 = article.get_attribute("href")
                article_urls.append(url2)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")
        if i != 3:
            try:
                return article_urls + get_article_urls(f"{origin_url}/page/{i+2}",origin_url, driver, i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvée, retourner les URLs d'articles actuels
                print("'la page suivante' n'a pas été trouvée.")
                return article_urls
        else:
            return article_urls
        
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles : {e}")
        return []



def get_article_info(url, date_format, driver):
    """
    Cette fonction récupère les informations d'un article à partir de son URL.

    Args:
        url (str): L'URL de l'article.
        date_format (str): Le format de date spécifié.
        driver: Le WebDriver pour le navigateur.

    Returns:
        dict: Un dictionnaire contenant les détails de l'article.
    """
    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.layout-section div")))
        article = driver.find_element(By.CSS_SELECTOR, "div.layout-section div")
        
        title = ""
        date = ""
        tag = ""
        description1 = ""
        description2 = ""

        try:
            date = article.find_element(By.CSS_SELECTOR, "div.subheadline-date").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de la date : {e}")
        
        if date_format in date:
            # Essayer de trouver chaque élément et assigner les valeurs
            try:
                title = article.find_element(By.CSS_SELECTOR, "section.main div div:nth-child(1) div div h1").text.strip()
            except Exception as e:
                print(f"Erreur lors de la récupération du titre : {e}")
        
            try:
                tag_element = article.find_element(By.CSS_SELECTOR, "section.main div div:nth-child(2) div section.col-sm-12.col-md-12.col-xl-9.col-lg-9.article-main-padding div div.le360-tags-holder")
                tag = tag_element.text.strip()
            except NoSuchElementException as e:
                # Si l'élément tag n'est pas trouvé, laisser tag vide
                print("L'élément 'tag' n'a pas été trouvé.")
            
            # Récupérer les descriptions
            try:
                description2_element = article.find_element(By.CSS_SELECTOR, "section.main div div:nth-child(2) div section.col-sm-12.col-md-12.col-xl-9.col-lg-9.article-main-padding div article")
                description2 = description2_element.text.strip()
            except NoSuchElementException as e:
                # Si l'élément description1 n'est pas trouvé, laisser la description1 vide
                print("L'élément 'description2' n'a pas été trouvé.")
            
            try:
                description1_element = article.find_element(By.CSS_SELECTOR, "section.main div div:nth-child(2) div section.col-sm-12.col-md-12.col-xl-9.col-lg-9.article-main-padding div h2")
                description1 = description1_element.text.strip()
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
                    "source_link": "https://fr.le360.ma/"
                }
            elif description1:
                article_info = {
                    "titre": title,
                    "description": description1,
                    "date": date,
                    "tag": tag,
                    "source_link": "https://fr.le360.ma/"
                }
            elif description2:
                article_info = {
                    "titre": title,
                    "description": description2,
                    "date": date,
                    "tag": tag,
                    "source_link": "https://fr.le360.ma/"
                }
            else:
                article_info = {
                    "titre": title,
                    "description": "",
                    "date": date,
                    "tag": tag,
                    "source_link": "https://fr.le360.ma/"
                }
            
            return article_info
        else:
            return None
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None










def main2(date,driver):
    """
    Fonction principale pour récupérer les articles et les stocker dans un fichier Excel.

    Args:
        date (str): La date au format "JJ-MM-AAAA".
    """
    # Initialiser le WebDriver (en utilisant Firefox dans cet exemple)

    try:
        date_format = "/".join(date.split("-"))

        # Récupérer la page web principale
        driver.get("https://fr.le360.ma/")
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.layout-section div header div.header-menu-bar")))

        menu = driver.find_element(By.CSS_SELECTOR, "div.layout-section div header div.header-menu-bar div div")
        categories_url = get_categories_url(menu)

        news_list = []
        for category_url in categories_url:
            article_urls = get_article_urls(category_url,category_url, driver,0)
            for url in tqdm(article_urls, desc=f"Progression dans la url '{category_url}'"):
                article_info = get_article_info(url, date_format, driver)
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
        print(f"Une erreur s'est produite lors de l'exécution du programme : {e}")
        
