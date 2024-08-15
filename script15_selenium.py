from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation
from function_basics import change_date_strucutre  # Fonction pour changer le format de la date
from selenium.common.exceptions import NoSuchElementException

def get_article_urls(category_url,origin_url, driver, date, i):
    """
    Cette fonction récupère les URLs des articles d'une catégorie spécifique pour une date donnée.

    Args:
        category_url (str): L'URL de la catégorie d'articles.
        driver: Le WebDriver pour le navigateur.
        date (str): La date recherchée dans les articles.
        i (int): Le numéro de la page en cours.

    Returns:
        list: Une liste des URLs d'articles pour la date spécifiée.
    """
    article_urls = []


    try:
        # Récupérer la page web pour la catégorie donnée
        driver.get(category_url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.elementor.elementor-114293.elementor-location-archive > section > div > div.elementor-column.elementor-col-50.elementor-top-column.elementor-element.elementor-element-d1d7e69 > div > div.elementor-element.elementor-element-af753b5.elementor-grid-2.elementor-grid-tablet-2.elementor-grid-mobile-1.elementor-posts--thumbnail-top.elementor-card-shadow-yes.elementor-posts__hover-gradient.elementor-widget.elementor-widget-posts > div > div.elementor-posts-container.elementor-posts.elementor-posts--skin-cards.elementor-grid.elementor-posts-masonry")))

        # Récupérer les éléments de la liste d'articles
        articles = driver.find_elements(By.CSS_SELECTOR, "body > div.elementor.elementor-114293.elementor-location-archive > section > div > div.elementor-column.elementor-col-50.elementor-top-column.elementor-element.elementor-element-d1d7e69 > div > div.elementor-element.elementor-element-af753b5.elementor-grid-2.elementor-grid-tablet-2.elementor-grid-mobile-1.elementor-posts--thumbnail-top.elementor-card-shadow-yes.elementor-posts__hover-gradient.elementor-widget.elementor-widget-posts > div > div.elementor-posts-container.elementor-posts.elementor-posts--skin-cards.elementor-grid.elementor-posts-masonry > article ")

        for article in articles:
            try:
                datee = article.find_element(By.CSS_SELECTOR, "div.elementor-post__meta-data > span").text.strip()
                # Vérifier si la date recherchée est présente dans la date de l'article
                if date in datee:
                    url = article.find_element(By.CSS_SELECTOR, "div.elementor-post__text > h3 > a").get_attribute("href")
                    article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")

        if i != 3:
            try:
                return article_urls + get_article_urls(f"{origin_url}page/{i+2}",origin_url, driver, date, i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvée, retourner les URLs d'articles actuels
                print("'la page suivante' n'a pas été trouvée.")
                return article_urls
        else:
            return article_urls
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs ou la page n'exist pas des articles de la catégorie '{category_url}'")

    return article_urls


def get_article_info(url, driver, date_format):
    """
    Cette fonction récupère les informations d'un article à partir de son URL.

    Args:
        url (str): L'URL de l'article.
        driver: Le WebDriver pour le navigateur.
        date_format (str): Le format de la date à utiliser.

    Returns:
        dict: Un dictionnaire contenant les détails de l'article.
    """
    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]")))
        # Récupérer les éléments nécessaires
        article = driver.find_element(By.XPATH, "/html/body/div[2]/section[1]/div/div/div")

       
        title = ""
        tag = ""
        description1 = ""
        description2 = ""
        
        # Essayer de trouver chaque élément et assigner les valeurs
        try:
            title = article.find_element(By.CSS_SELECTOR, "div.elementor-widget-container h1.elementor-heading-title ").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")
        
        try:
            description1 = article.find_element(By.CSS_SELECTOR , "div.elementor-element.elementor-element-aea8485.elementor-widget.elementor-widget-theme-post-excerpt > div").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération description1 : {e}")
            
        try:
            description2 = article.find_element(By.CSS_SELECTOR, "div.elementor-element.elementor-element-b869541.elementor-widget.elementor-widget-theme-post-content > div").text.strip()
            
        except Exception as e:
            print(f"Erreur lors de la récupération de la description2 : {e}")
        
        article_info = {
            "titre": title,
            "description": f"{description1} {description2}",
            "date": date_format,
            "tag" : tag,
            "source_link": "https://perspectivesmed.com/"
        }
        
        return article_info
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None
    
def get_categories_url(menu):
    """
    Cette fonction récupère les URLs des catégories à partir du menu du site Web.

    Args:
        menu: L'élément du menu contenant les catégories.

    Returns:
        list: Une liste des URLs des catégories.
    """
    categories_url = []

    category_items = menu.find_elements(By.CSS_SELECTOR , "li.menu-item > a")

    for i in range(len(category_items)):
        category = category_items[i].get_attribute("href")
        if category:
            categories_url.append(category)
    
    return categories_url

def main15(date,driver):
    source ="https://perspectivesmed.com/"
    """
    Fonction principale pour récupérer les articles et les stocker dans un fichier Excel.

    Args:
        date (str): La date recherchée pour les articles.
        source (str): L'URL du site Web à analyser.
    """

   
    try:
        # Convertir la date en un format utilisé par le site Web pour la recherche
        date_format = change_date_strucutre(date).lower()
        print(date_format)
        # Récupérer la page web principale
        driver.get(source)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#menu-1-be6096f")))
        
        menu = driver.find_element(By.CSS_SELECTOR, "#menu-1-be6096f")
        # Appeler la fonction get_categories pour obtenir la liste des catégories
        categories_url = get_categories_url(menu)

        news_list = []
        for i in range(1, len(categories_url)):
            article_urls = get_article_urls(categories_url[i],categories_url[i], driver, date_format,0)
            for url in tqdm(article_urls, desc=f"Progression dans la catégorie '{categories_url[i]}'"):
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
        print(f"Une erreur s'est produite lors de la récupération https://perspectivesmed.com/ : {e}")
