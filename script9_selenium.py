from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation
from function_basics import change_date_maj  # Fonction pour changer le format de la date
from selenium.common.exceptions import NoSuchElementException

def get_article_urls(category_url, driver,i):
    """
    Cette fonction récupère les URLs des articles d'une catégorie spécifique.

    Args:
        category_url (str): L'URL de la catégorie d'articles.
        driver: Le WebDriver pour le navigateur.

    Returns:
        list: Une liste des URLs d'articles pour la catégorie donnée.
    """
    article_urls = []

    try:
        # Récupérer la page web pour la catégorie donnée
        driver.get(category_url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.page2_rubrique  div")))

        # Récupérer les éléments de la liste d'articles
        articles = driver.find_elements(By.CSS_SELECTOR, "div.rub > h3 > a")

        for article in articles:
            try:
                url = article.get_attribute("href")
                article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")
        if i != 4:
            try:
                page = driver.find_element(By.CSS_SELECTOR, "div.cel1.forpager > div > a:nth-child(6)")
                page_url = page.get_attribute("href")
                return article_urls + get_article_urls(page_url, driver, i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvé, return article_urls
                print("'la page suivante' n'a pas été trouvé.")
                return article_urls
        else:
            return article_urls
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles de la catégorie '{category_url}' : {e}")
        return []


def get_article_info(url, driver, date_format):
    """
    Cette fonction récupère les informations d'un article à partir de son URL.

    Args:
        url (str): L'URL de l'article.
        driver: Le WebDriver pour le navigateur.
        date_format (str): Le format de la date recherchée.

    Returns:
        dict: Un dictionnaire contenant les détails de l'article.
    """
    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#z_col1 > div")))
        # Récupérer les éléments nécessaires
        article = driver.find_element(By.CSS_SELECTOR, "#z_col1 > div")
    
        title = ""
        date = ""
        tag = ""
        description1 = ""
        description2 = ""
        
        try:
            date = article.find_element(By.CSS_SELECTOR, "div.cel1 div:nth-child(5) > div").text.strip().replace(""," ")
            
        except NoSuchElementException as e:
            # Si l'élément description1 n'est pas trouvé, laisser la description1 vide
            print("L'élément 'date' n'a pas été trouvé.")
            
        if f" {date_format}" in date :        
            # Essayer de trouver chaque élément et assigner les valeurs
            try:
                title = article.find_element(By.CSS_SELECTOR, "div.titre > h1").text.strip().replace(""," ")
            except Exception as e:
                print(f"Erreur lors de la récupération du titre : {e}")
        
            # Récupérer les descriptions
            try:
                description2_element = article.find_element(By.CSS_SELECTOR, "div.texte")
                description2 = description2_element.text.strip().replace(""," ")
            except NoSuchElementException as e:
                # Si l'élément description1 n'est pas trouvé, laisser la description1 vide
                print("L'élément 'description2' n'a pas été trouvé.")
            
            try:
                description1_element = article.find_element(By.CSS_SELECTOR, "div.chapeau > h3")
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
                    "tag" : tag,
                    "source_link": "https://www.lopinion.ma/"
                }
            elif description1:
                article_info = {
                    "titre": title,
                    "description": description1,
                    "date": date,
                    "tag" : tag,
                    "source_link": "https://www.lopinion.ma/"
                }
            elif description2:
                article_info = {
                    "titre": title,
                    "description": description2,
                    "date": date,
                    "tag" : tag,
                    "source_link": "https://www.lopinion.ma/"
                }
            else:
                article_info = {
                    "titre": title,
                    "description": "",
                    "date": date,
                    "tag" : tag,
                    "source_link": "https://www.lopinion.ma/"
                }
            
            return article_info
        else:
            return None
        
        
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

    category_items = menu.find_elements(By.CSS_SELECTOR , "ul.menu_ligne   li  ul  li  a")
    for i in range(1,len(category_items)):
        category = category_items[i].get_attribute("href")
        if category:
            categories_url.append(category)
    
    return categories_url

def main9(date,driver):
    """
    Fonction principale pour récupérer les articles et les stocker dans un fichier Excel.

    Args:
        date (str): La date recherchée pour les articles.
    """
    source ="https://www.lopinion.ma/"

   
    try:
        date_format = change_date_maj(date)
        # Récupérer la page web principale
        driver.get(source)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "mod_49480176")))
        

        menu = driver.find_element(By.ID, "mod_49480176")
        # Appeler la fonction get_categories pour obtenir la liste des catégories

        categories_url = get_categories_url(menu)

        
        
        news_list = []
        for category_url in categories_url:
            article_urls = get_article_urls(category_url, driver,0)
            for url in tqdm(article_urls, desc=f"Progression dans la url '{category_url}'"):
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
        print(f"Une erreur s'est produite lors de la récupération https://www.lopinion.ma/ ' : {e}")
