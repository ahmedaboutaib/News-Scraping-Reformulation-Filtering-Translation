from selenium import webdriver  # Pour automatiser les interactions avec un navigateur Web
from selenium.webdriver.common.by import By  # Pour trouver des éléments par différents sélecteurs
from selenium.webdriver.support.ui import WebDriverWait  # Pour attendre que certains éléments se chargent
from selenium.webdriver.support import expected_conditions as EC  # Pour définir des conditions d'attente
import pandas as pd  # Pour manipuler des données sous forme de DataFrame
from tqdm import tqdm  # Pour afficher une barre de progression
import os  # Pour interagir avec le système d'exploitation
from function_basics import change_date_maj  # Fonction pour changer le format de la date
from selenium.common.exceptions import NoSuchElementException

def get_article_urls(category_url,origin_url, driver, date_format,i):
    """
    Cette fonction récupère les URLs des articles d'une catégorie spécifique.

    Args:
        category_url (str): L'URL de la catégorie d'articles.
        driver: Le WebDriver pour le navigateur.
        date_format (str): Le format de la date recherchée.

    Returns:
        list: Une liste des URLs d'articles pour la catégorie donnée.
    """
    article_urls = []

    try:
        # Récupérer la page web pour la catégorie donnée
        driver.get(category_url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.options_layout_wrapper.jl_clear_at > div > div.jl_block_content > div > div.jlc-row > div.jlc-col-md-8.jl_main_achv.jl_achv_tpl_list > div.jl_clear_at.block-section.jl-main-block.jl_wrapper_cat > div > div > div > div")))

        # Récupérer les éléments de la liste d'articles
        articles = driver.find_elements(By.CSS_SELECTOR, "body > div.options_layout_wrapper.jl_clear_at > div > div.jl_block_content > div > div.jlc-row > div.jlc-col-md-8.jl_main_achv.jl_achv_tpl_list > div.jl_clear_at.block-section.jl-main-block.jl_wrapper_cat > div > div > div > div > div > div.jl_fe_text")

        for article in articles:
            try:
                url = article.find_element(By.CSS_SELECTOR, "h3 > a").get_attribute("href")
                date = article.find_element(By.CSS_SELECTOR, "span.jl_post_meta > span.post-date").text.strip()
                if date == date_format:
                    article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")

        if i != 3:
            try:
                return article_urls + get_article_urls(f"{origin_url}/page/{i+2}",origin_url, driver, date_format, i + 1)
            except NoSuchElementException as e:
                # Si la page suivante n'est pas trouvée, retourner les URLs d'articles actuels
                print("'la page suivante' n'a pas été trouvée.")
                return article_urls
        else:
            return article_urls
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des URLs des articles de la catégorie '{category_url}' : {e}")

    return article_urls


def get_article_info(url, driver):
    """
    Cette fonction récupère les informations d'un article à partir de son URL.

    Args:
        url (str): L'URL de l'article.
        driver: Le WebDriver pour le navigateur.

    Returns:
        dict: Un dictionnaire contenant les détails de l'article.
    """
    try:
        # Récupérer la page web pour l'article spécifique
        driver.get(url)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jlc-col-md-8.jl_smmain_con > div > div")))
        # Récupérer les éléments nécessaires
        article = driver.find_element(By.CSS_SELECTOR, "div.jlc-col-md-8.jl_smmain_con > div > div")

        title = ""
        date = ""
        tag = ""
        description = ""
     

        try:
            date = article.find_element(By.CSS_SELECTOR, "div.jl_shead_tpl1 > div.jl_shead_tpl_txt > div > span > span.post-date").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de la date : {e}")

        # Essayer de trouver chaque élément et assigner les valeurs
        try:
            title = article.find_element(By.CSS_SELECTOR, "div.jl_shead_tpl1 > div.jl_shead_tpl_txt > h1").text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération du titre : {e}")

        try:
            description = " ".join([p.text.strip() for p in article.find_elements(By.CSS_SELECTOR, "div.post_content_w > div.jls_con_w > div p")]) 
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")

        article_info = {
            "titre": title.replace(""," ").replace(""," "),
            "description": description.replace(""," ").replace(""," "),
            "date": date.replace(""," ").replace(""," "),
            "tag": tag.replace(""," ").replace(""," "),
            "source_link": "https://aujourdhui.ma"
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

    category_items = menu.find_elements(By.CSS_SELECTOR, "li  a")
    for i in range(1, len(category_items)):
        category = category_items[i].get_attribute("href")
        if category:
            categories_url.append(category)

    return categories_url


def main19(date,driver):
    """
    Fonction principale pour récupérer les articles et les stocker dans un fichier Excel.

    Args:
        date (str): La date recherchée pour les articles.
    """
    source = "https://aujourdhui.ma"
    # Initialiser le WebDriver (en utilisant Firefox dans cet exemple)
 

    try:
        date_format = change_date_maj(date).upper()
        # Récupérer la page web principale
        driver.get(source)
        # Attendre que les éléments se chargent
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "menu-main")))

        menu = driver.find_element(By.ID, "menu-main")
        # Appeler la fonction get_categories pour obtenir la liste des catégories

        categories_url = get_categories_url(menu)

        news_list = []
        for i in range(len(categories_url) - 1):
            article_urls = get_article_urls(categories_url[i],categories_url[i], driver, date_format,0)
            for url in tqdm(article_urls, desc=f"Progression dans la url '{categories_url[i]}'"):
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
        print(f"Une erreur s'est produite lors de la récupération https://aujourdhui.ma ' : {e}")
