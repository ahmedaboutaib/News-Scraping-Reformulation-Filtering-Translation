from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation
from function_basics import change_date_maj  # Importer une fonction personnalisée pour changer le format de date
from selenium.common.exceptions import NoSuchElementException

def get_article_urls(category_url, driver, date_format,i):
    """
    Cette fonction récupère les URLs des articles d'une catégorie spécifique.

    Args:
        category_url (str): L'URL de la catégorie d'articles.
        driver: Le WebDriver pour le navigateur.
        date_format (str): Le format de date spécifié.

    Returns:
        list: Une liste des URLs d'articles conformes au format de date spécifié.
    """
    article_urls = []
    try:
        # Récupérer la page web pour la catégorie donnée
        driver.get(category_url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#block-system-main > div > div")))
        if i == 0 :
            # Récupérer l'URL et la date du premier article en vedette
            try:
                url0 = driver.find_element(By.CSS_SELECTOR, "#views-bootstrap-grid-1 > div > div > div.content_une.col.col-xs-12.col-lg-12 > span.field-content > h2 > a").get_attribute("href")
                date0 = driver.find_element(By.CSS_SELECTOR, "#views-bootstrap-grid-1 > div > div > div.content_une.col.col-xs-12.col-lg-12 > span.legende_rubrique > div > span.date-display-single").text.strip()
                if date_format in date0:
                    article_urls.append(url0)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")

        # Récupérer les URLs et dates des autres articles
        articles1 = driver.find_elements(By.CSS_SELECTOR, "#views-bootstrap-grid-2 > div.row > div.col-xs-12")
        for article in articles1:
            try:
                url1 = article.find_element(By.CSS_SELECTOR, "span.field-content h2 a").get_attribute("href")
                date1 = article.find_element(By.CSS_SELECTOR, "span.date-display-single").text.strip()
                if date_format in date1:
                    article_urls.append(url1)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")

        if i != 4:
            try:
                page = driver.find_element(By.CSS_SELECTOR, "#block-system-main > div > div > div > div.une_rubrique > div > div.text-center > ul > li.next > a")
                page_url = page.get_attribute("href")
                return article_urls + get_article_urls(page_url,driver, date_format, i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvé, return article_urls
                print("'la page suivante' n'a pas été trouvé.")
                return article_urls
        else:
            return article_urls

    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles : {e}")
        return None


def get_article_info(url, driver, date_format):
    """
    Cette fonction récupère les informations d'un article à partir de son URL.

    Args:
        url (str): L'URL de l'article.
        driver: Le WebDriver pour le navigateur.
        date_format (str): Le format de date spécifié.

    Returns:
        dict: Un dictionnaire contenant les détails de l'article.
    """
    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#content_leconomiste")))
        # Récupérer les éléments nécessaires
        article = driver.find_element(By.CSS_SELECTOR, "#content_leconomiste")

        title = ""
        tag = ""
        description = ""

        # Essayer de trouver chaque élément et assigner les valeurs
        try:
            title = article.find_element(By.CSS_SELECTOR, "h1").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")

        '''
        try:
            tag = article.find_element(By.CLASS_NAME, "tagcloud").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération des tags : {e}")
        '''

        try:
            description = article.find_element(By.CSS_SELECTOR, "p").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")

        article_info = {
            "titre": title.replace(""," "),
            "description": description.replace(""," "),
            "date": date_format.replace(""," "),
            "tag": tag.replace(""," "),
            "source_link": "https://www.leconomiste.com/"
        }

        return article_info

    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None


def get_categories_url(menu):
    """
    Cette fonction extrait les URLs des catégories à partir du menu du site Web.

    Args:
        menu: L'élément du menu contenant les catégories.

    Returns:
        list: Une liste des URLs des catégories.
    """
    categories_url = []

    category_items = menu.find_elements(By.CSS_SELECTOR, "li.nav-item > a")
    for i in range(1, len(category_items)):
        category = category_items[i].get_attribute("href")
        if category:
            categories_url.append(category)

    return categories_url


def main10(date,driver):
    """
    Fonction principale pour récupérer les articles et les stocker dans un fichier Excel.

    Args:
        date (str): La date au format "JJ-MM-AAAA".
    """

    try:
        element = date.split("-")
        date_format = f"{element[0]}/{element[1]}/{element[2][2:]}"
        # Récupérer la page web principale
        driver.get("https://www.leconomiste.com/")
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#navbarNav > ul")))

        menu = driver.find_element(By.CSS_SELECTOR, "#navbarNav > ul")
        # Appeler la fonction get_categories pour obtenir la liste des catégories
        categories_url = get_categories_url(menu)

        news_list = []
        for i in range(4, len(categories_url) - 3):
            article_urls = get_article_urls(categories_url[i], driver, date_format,0)
            for url in tqdm(article_urls, desc=f"Progression dans la url '{categories_url[i]}'"):
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
        print(f"Une erreur s'est produite lors de la récupération https://www.leconomiste.com/ ' : {e}")
