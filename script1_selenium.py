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

        category_items = menu.find_elements(By.CSS_SELECTOR, "li > a")
        for i in range(2, len(category_items) ):
            category = category_items[i].get_attribute("href")
            if category:
                categories_url.append(category)

        return categories_url
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs de catégorie : {e}")
        return []

def get_article_urls(category_url, driver, i):
    """
    Cette fonction récupère les URLs des articles d'une catégorie spécifique.

    Args:
        category_url (str): L'URL de la catégorie d'articles.
        driver: Le WebDriver pour le navigateur.
        i (int): Un compteur pour limiter la récursion.

    Returns:
        list: Une liste des URLs d'articles.
    """
    try:
        article_urls = []

        # Récupérer la page web pour la catégorie donnée
        driver.get(category_url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#posts-container")))

        # Récupérer les URLs des autres articles
        articles = driver.find_elements(By.CSS_SELECTOR, "#posts-container > li")
        
        
        for article in articles:
            try:
                date = article.find_element(By.CSS_SELECTOR, "div > div > span.date.meta-item.tie-icon").text.strip()
                if "ساعات" in date or "ساعة" in date :
                    url = article.find_element(By.CSS_SELECTOR, "div > h2 > a").get_attribute("href")
                    article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")

        if i != 5:
            try:
                page = driver.find_element(By.CSS_SELECTOR, "#main-content-row > div > div.pages-nav > div > span.last-page.first-last-pages > a")
                page_url = page.get_attribute("href")
                return article_urls + get_article_urls(page_url, driver, i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvé, return article_urls
                print("'la page suivante' n'a pas été trouvé.")
                return article_urls
        else:
            return article_urls
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles : {e}")
        return []  # Retourner une liste vide en cas d'erreur

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
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#the-post")))
        article = driver.find_element(By.CSS_SELECTOR, "#the-post")
        
        title = ""
        tag = ""
        description = ""



        # Essayer de trouver chaque élément et assigner les valeurs
        try:
            title = article.find_element(By.CSS_SELECTOR, "header > div > h1").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")
        '''
        try:
            tag = article.find_element(By.CSS_SELECTOR, "section.main div div:nth-child(2) div section.col-sm-12.col-md-12.col-xl-9.col-lg-9.article-main-padding div div.le360-tags-holder").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du tag : {e}")
        '''
        # Récupérer la description
        try:
            description = " ".join([p.text.strip() for p in article.find_elements(By.CSS_SELECTOR, "div.entry-content.entry.clearfix   p")])
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")
        
        
        article_info = {
            "titre": title,
            "description": description,
            "date": date_format,
            "tag": tag,
            "source_link": "https://detafour.ma/"
        }
        
        return article_info
       
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None












def main1(date,driver):
    """
    Fonction principale pour récupérer les articles et les stocker dans un fichier Excel.

    Args:
        date (str): La date au format "JJ-MM-AAAA".
    """


    try:
        date_format = "/".join(date.split("-"))

        # Récupérer la page web principale
        driver.get("https://detafour.ma/")
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#menu-nav-menu")))

        menu = driver.find_element(By.CSS_SELECTOR, "#menu-nav-menu")
        categories_url = get_categories_url(menu)
        '''
        L  = get_article_urls(categories_url[0],driver,0)
        print(len(L))
        print(L)
        
        '''
        news_list = []
        for category_url in categories_url:
            article_urls = get_article_urls(category_url, driver,0)
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
        if not df.empty:
            # Définir l'ordre des colonnes
            df = df[['titre', 'description', 'date', 'tag', 'source_link']]
            # Exporter le DataFrame vers un fichier Excel
            df.to_excel(f'{date}.xlsx', index=False)
            print(f"Les données ont été exportées avec succès vers '{date}.xlsx'.")
        else:
            print("Le DataFrame est vide. Aucun fichier Excel n'a été créé.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'exécution https://detafour.ma/ : {e}")
