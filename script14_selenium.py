from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation



def get_article_urls(category_url, driver, date):
    """
    Cette fonction récupère les URLs des articles d'une catégorie spécifique pour une date donnée.

    Args:
        category_url (str): L'URL de la catégorie d'articles.
        driver: Le WebDriver pour le navigateur.
        date (str): La date recherchée dans les articles.

    Returns:
        list: Une liste des URLs d'articles pour la date spécifiée.
    """
    article_urls = []

    try:
        # Récupérer la page web pour la catégorie donnée
        driver.get(category_url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#z_col2 > div")))

        # Récupérer les éléments de la liste d'articles
        articles = driver.find_elements(By.CSS_SELECTOR, "#z_col2 > div > div.wm-module ul.xml")

        for article in articles:
            try:
                datee = article.find_element(By.CLASS_NAME, "date").text.strip()
                url = article.find_element(By.CSS_SELECTOR, "h3.titre > a").get_attribute("href")
                if date in datee:
                    article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")

    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles de la catégorie '{category_url}' : {e}")

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
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#z_col2 > div > div.wm-module")))
        # Récupérer les éléments nécessaires
        article = driver.find_element(By.CSS_SELECTOR, "#z_col2 > div > div.wm-module")
       
        title = ""
        date = ""
        tag = ""
        description1 = ""
        description2 = ""
        
        # Essayer de trouver chaque élément et assigner les valeurs
        try:
            title = article.find_element(By.CSS_SELECTOR, "div.titre > h1").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")

        try:
            description2 = article.find_element(By.CSS_SELECTOR, "#para_1 > div.texte").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")

        article_info = {
            "titre": title,
            "description": f"{description2}",
            "date": date_format,
            "tag": tag,
            "source_link": "https://www.hcp.ma/"
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

    category_items = menu.find_elements(By.CSS_SELECTOR , "a.themes_block")

    for i in range(len(category_items)):
        category = category_items[i].get_attribute("href")
        if category:
            categories_url.append(category)
    
    return categories_url

def main14(date,driver):
    source = "https://www.hcp.ma/"
    """
    Fonction principale pour récupérer les articles et les stocker dans un fichier Excel.

    Args:
        date (str): La date recherchée pour les articles.
        source (str): L'URL du site Web à analyser.
    """

   
    try:
        date_format = "/".join(date.split("-"))
        # Récupérer la page web principale
        driver.get(source)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#z_col1 > div.z_col_median.z_col1_inner > div:nth-child(1) > div > div > div.hcp_home_themes_container")))
        
        menu = driver.find_element(By.CSS_SELECTOR, "#z_col1 > div.z_col_median.z_col1_inner > div:nth-child(1) > div > div > div.hcp_home_themes_container")
        # Appeler la fonction get_categories pour obtenir la liste des catégories
        categories_url = get_categories_url(menu)

        news_list = []
        for i in range(len(categories_url)-1):
            article_urls = get_article_urls(categories_url[i], driver, date_format)
            for url in tqdm(article_urls, desc=f"Scraping des articles dans la catégorie '{categories_url[i]}'"):
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
        print(f"Une erreur s'est produite lors de la récupération https://www.hcp.ma/ ' : {e}")
