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
    Cette fonction récupère les URLs des catégories à partir du menu du site Web.

    Args:
        menu: L'élément du menu contenant les catégories.

    Returns:
        list: Une liste des URLs des catégories.
    """
    categories_url = []

    category_items = menu.find_elements(By.CSS_SELECTOR , "nav.main-menu__nav li a")
    for i in range(1,len(category_items)-1):
        category = category_items[i].get_attribute("href")
        if category:
            categories_url.append(category)
    
    return categories_url

def get_article_urls(category_url, driver, date,i):
    """
    Cette fonction récupère les URLs des articles d'une catégorie spécifique.

    Args:
        category_url (str): L'URL de la catégorie d'articles.
        driver: Le WebDriver pour le navigateur.
        date (str): La date recherchée pour les articles.

    Returns:
        list: Une liste des URLs d'articles pour la catégorie donnée.
    """
    try:
        article_urls = []

        # Récupérer la page web pour la catégorie donnée
        driver.get(category_url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.rt-left-sidebar-sapcer-5 > div > div")))

        # Récupérer les éléments de la liste d'articles
        articles = driver.find_elements(By.CSS_SELECTOR, "div.rt-left-sidebar-sapcer-5 > div > div ")
    

        for article in articles:
            try:

                url = article.find_element(By.CSS_SELECTOR, "h3.post-title a").get_attribute("href")

                article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")
        if i != 4:
            try:
                page = driver.find_elements(By.CSS_SELECTOR, "#main_content > main > section > div > div > div.col-xl-9.sticky-coloum-item > div > div.rt-left-sidebar-sapcer-5 > nav > ul > li > a")
                page_url = page[len(page)-1].get_attribute("href")
                return article_urls + get_article_urls(page_url, driver,date, i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvé, return article_urls
                print("'la page suivante' n'a pas été trouvé.")
                return article_urls
        else:
            return article_urls
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles : {e}")
        return []  # Retourner une liste vide en cas d'erreur


def get_article_info(url, date, driver):
    """
    Cette fonction récupère les informations d'un article à partir de son URL.

    Args:
        url (str): L'URL de l'article.
        date (str): La date recherchée pour les articles.
        driver: Le WebDriver pour le navigateur.

    Returns:
        dict: Un dictionnaire contenant les détails de l'article.
    """
    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rt-main-post-single")))
        # Récupérer les éléments nécessaires
        article = driver.find_element(By.CLASS_NAME, "rt-main-post-single")
        
        title = ""
        datee = ""
        tag = ""
        description = ""
        
        
                # Essayer de trouver chaque élément et assigner les valeurs
        try:
            datee = article.find_element(By.CSS_SELECTOR, "div.post-header > div > ul > li:nth-child(2) > span").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du date : {e}")
        if date == datee :        
            # Essayer de trouver chaque élément et assigner les valeurs
            try:
                title = article.find_element(By.CLASS_NAME, "title").text.strip()
            except Exception as e:
                print(f"Erreur lors de la récupération du titre : {e}")
            
            try:
                description =  " ".join([p.text.strip() for p in article.find_elements(By.CSS_SELECTOR, "div.post-body p")])
            except Exception as e:
                print(f"Erreur lors de la récupération description1 : {e}")
            
            ''' 
            try:
                tag = article.find_element(By.CSS_SELECTOR, "div.elementor-element.elementor-element-b869541.elementor-widget.elementor-widget-theme-post-content > div").text.strip()
                
            except Exception as e:
                print(f"Erreur lors de la récupération de tag : {e}")
            '''
            try:
                tag_element = article.find_element(By.CLASS_NAME, "tag-list")
                tag = tag_element.text.strip()
            except NoSuchElementException as e:
                # Si l'élément tag n'est pas trouvé, laisser tag vide
                print("L'élément 'tag' n'a pas été trouvé.")           
            
            article_info = {
                "titre": title,
                "description": description,
                "date": datee,
                "tag" : tag,
                "source_link": "https://www.maroc-hebdo.press.ma/"
            }
            return article_info
        else:
            return None
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None

def main6(date,driver):
    """
    Fonction principale pour récupérer les articles et les stocker dans un fichier Excel.

    Args:
        date (str): La date recherchée pour les articles.
    """


    try:
        # Récupérer la page web principale
        driver.get("https://www.maroc-hebdo.press.ma/")
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "main-menu__nav")))
        
        menu = driver.find_element(By.CLASS_NAME, "main-menu__nav")
        # Appeler la fonction get_categories pour obtenir la liste des catégories

        categories_url = get_categories_url(menu)

        news_list = []
        for category_url in categories_url:
            article_urls = get_article_urls(category_url, driver, date,0)
            for url in tqdm(article_urls, desc=f"Progression dans la url '{category_url}'"):
                article_info = get_article_info(url, date, driver)
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
        print(f"Une erreur s'est produite lors de la récupération https://www.maroc-hebdo.press.ma/ ' : {e}")

