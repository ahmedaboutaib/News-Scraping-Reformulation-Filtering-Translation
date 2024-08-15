import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation
from selenium.common.exceptions import NoSuchElementException

def get_categories_url(menu, donne_web):
    """
    Cette fonction extrait les URLs des catégories à partir du menu du site Web.

    Args:
        menu: L'élément du menu contenant les catégories.
        donne_web (dict): Les informations de la configuration.

    Returns:
        list: Une liste des URLs des catégories.
    """
    categories_url = []
    category_items = menu.find_elements(By.CSS_SELECTOR, donne_web["CSS_SELECTOR_categoy"])
    for i in range(1, len(category_items)):
        category = category_items[i].get_attribute("href")
        if category and donne_web["source"] in category:
            categories_url.append(category)
    return categories_url


def get_article_urls(category_url, driver, donne_web,i):
    """
    Cette fonction récupère les URLs des articles d'une catégorie spécifique.

    Args:
        category_url (str): L'URL de la catégorie d'articles.
        driver: Le WebDriver pour le navigateur.
        donne_web (dict): Les informations de la configuration.

    Returns:
        list: Une liste des URLs d'articles.
    """


    try:
        article_urls = []

        # Récupérer la page web pour la catégorie donnée
        driver.get(category_url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, donne_web["CLASS_NAME_category_titles"])))

        # Récupérer les éléments de la liste d'articles
        articles = driver.find_elements(By.CLASS_NAME, donne_web["CLASS_NAME_category_titles"])

        for article in articles:
            try:
                date = article.find_element(By.CLASS_NAME, donne_web["CLASS_NAME_date"]).text.strip()
                url = article.find_element(By.CSS_SELECTOR, donne_web["CSS_SELECTOR_title_rul"]).get_attribute("href")
                date_format = " ".join(date.split()[:3]).upper()
        
                if date_format == donne_web["date"]:
                    article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")
        
        if i != 2:
            try:
                page = driver.find_element(By.CSS_SELECTOR, "#main-content-row > div > div.pages-nav > div > span.last-page.first-last-pages > a")
                page_url = page.get_attribute("href")
                return article_urls + get_article_urls(page_url, driver, donne_web ,i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvé, return article_urls
                print("'la page suivante' n'a pas été trouvé.")
                return article_urls
        else:
            return article_urls
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles : {e}")
        return []  # Retourner une liste vide en cas d'erreur










def get_article_info(url, driver, donne_web):
    """
    Cette fonction récupère les informations d'un article à partir de son URL.

    Args:
        url (str): L'URL de l'article.
        driver: Le WebDriver pour le navigateur.
        donne_web (dict): Les informations de la configuration.

    Returns:
        dict: Un dictionnaire contenant les détails de l'article.
    """
    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, donne_web["ID_post"])))
        # Récupérer les éléments nécessaires
        
        article = driver.find_element(By.ID, donne_web["ID_post"])
        
        title = ""
        datee = ""
        tag = ""
        description = ""
        
        
                # Essayer de trouver chaque élément et assigner les valeurs
        try:
            datee = article.find_element(By.CLASS_NAME, donne_web["CLASS_NAME_date"]).text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du date : {e}")
        
        # Essayer de trouver chaque élément et assigner les valeurs
        try:
            title =  article.find_element(By.CLASS_NAME, donne_web["CLASS_NAME_title"]).text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")
        
        try:
            description_elements = article.find_elements(By.CSS_SELECTOR, donne_web["CSS_SELECTOR_description"])
            description = " ".join([p.text.strip() for p in description_elements ]).replace(""," ")
        except Exception as e:
            print(f"Erreur lors de la récupération description1 : {e}")
        try:
            tag_element = article.find_element(By.CLASS_NAME, donne_web["CLASS_NAME_TAG"])
            tag = tag_element.text.strip()
        except NoSuchElementException as e:
            print(f"Tag non trouvé pour l'article '{url}'")

        
        article_info = {
            "titre": title.replace(""," "),
            "description": description,
            "date": datee.replace(""," "),
            "tag" : tag.replace(""," "),
            "source_link": donne_web["source"]
        }        
    

        return article_info
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None


def main7(date,driver):
    date_format = "/".join(date.split("-"))
    donne_web ={
        "source": "https://leseco.ma/",
        "ID_menu_actegores": "menu-main",
        "CSS_SELECTOR_categoy": "li.menu-item a",
        "CLASS_NAME_category_titles": "post-item",
        "CSS_SELECTOR_title_rul": "h2.post-title a",
        "CLASS_NAME_date": "date",
        "ID_post": "the-post",
        "CLASS_NAME_title": "post-title",
        "CLASS_NAME_TAG": "tagcloud",
        "CSS_SELECTOR_description": "#the-post > div.entry-content.entry.clearfix > p",
        "date" : date_format
    }
    """
    Fonction principale pour récupérer les articles et les stocker dans un fichier Excel.

    Args:
        donne_web (dict): Les informations de la configuration.
    """


    try:
        # Récupérer la page web principale
        driver.get(donne_web["source"])
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, donne_web["ID_menu_actegores"])))

        menu = driver.find_element(By.ID, donne_web["ID_menu_actegores"])
        # Appeler la fonction get_categories pour obtenir la liste des catégories
        categories_url = get_categories_url(menu, donne_web)

        news_list = []
        for category_url in categories_url:
            article_urls = get_article_urls(category_url, driver, donne_web,0)
            for url in tqdm(article_urls, desc=f"Progression dans la url '{category_url}'"):
                article_info = get_article_info(url, driver, donne_web)
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
        print(f"Une erreur s'est produite lors de la récupération https://leseco.ma/ ' : {e}")

