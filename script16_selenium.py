from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from tqdm import tqdm
import os
from function_basics import change_date_arabic
import sys
from selenium.common.exceptions import NoSuchElementException



def get_article_urls(category_url,origin_url, driver, date,i):
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
        driver.get(category_url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main-page-content > div.posts-categoy.row > div")))

        articles = driver.find_elements(By.CSS_SELECTOR, "#main-page-content > div.posts-categoy.row > div")

        for article in articles:
            try:
                datee = article.find_element(By.CSS_SELECTOR, "div > div > div.card-body > div > div > span > small").text.strip()
               
                if f" {date}" in datee:
                    url = article.find_element(By.CSS_SELECTOR, "div > div > div.card-img-top > a").get_attribute("href")
                    article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")
      
        if i != 5:
            try:
                return article_urls + get_article_urls(f"{origin_url}/page/{i+2}",origin_url, driver, date, i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvée, retourner les URLs d'articles actuels
                print("'la page suivante' n'a pas été trouvée.")
                return article_urls
        else:
            return article_urls
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
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main-page-content > div > div.article-container > section article")))
        
        article = driver.find_element(By.CSS_SELECTOR, "#main-page-content > div > div.article-container > section > article")

        title = ""
        date = ""
        tag = ""
        description = ""
        
        try:
            # Récupération du titre de l'article
            title = article.find_element(By.CLASS_NAME, "post-title").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")
        
        try:
            # Récupération de la date de l'article
            date = article.find_element(By.CSS_SELECTOR , "span.date-post").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de la date : {e}")
        
        try:
            # Récupération de la description de l'article
            description = article.find_element(By.CLASS_NAME , "article-content").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")
        
        article_info = {
            "titre": title,
            "description": description,
            "date": date,
            "tag" : tag,
            "source_link": "https://www.hespress.com/"
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

def main16(date,driver):
    source = "https://www.hespress.com/"


   
    try:
        date_format = change_date_arabic(date)
      

        driver.get(source)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#menu-main_menu")))
        
        menu = driver.find_element(By.CSS_SELECTOR, "#menu-main_menu")
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
        print(f"Une erreur s'est produite lors de la récupération https://www.hespress.com/ ' : {e}")
