from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from tqdm import tqdm
import os
from selenium.common.exceptions import NoSuchElementException

def get_article_urls(url, driver, i):
    """
    Cette fonction récupère les URLs des articles d'une catégorie spécifique.

    Args:
        date (str): La date de la catégorie d'articles.
        driver: Le WebDriver pour le navigateur.
        i (int): Un compteur pour limiter la récursion.

    Returns:
        list: Une liste des URLs d'articles.
    """
    try:
        article_urls = []
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#box > div.row.hero-section.categoryPostsList > div.col-gold-lg > div ")))
        articles = driver.find_elements(By.CSS_SELECTOR, "#box > div.row.hero-section.categoryPostsList > div.col-gold-lg > div > div > article > div.text-zone > a")

        for article in articles:
            try:
                url = article.get_attribute("href")
                article_urls.append(url)
            except Exception as e:
                print(f"Une erreur s'est produite lors de la récupération de l'URL de l'article : {e}")

    
        if i != 10:
            try:
                page = driver.find_element(By.CSS_SELECTOR, "#box > div.row.hero-section.categoryPostsList > div.col-gold-lg > div > div.pagination.wp-pagenavi > a.next.page-numbers")
                page_url = page.get_attribute("href")
                return article_urls + get_article_urls(page_url, driver, i + 1)
            except NoSuchElementException as e:
                print("'la page suivante' n'a pas été trouvé.")
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
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#box > div.row.hero-section > div > div > article")))
        article = driver.find_element(By.CSS_SELECTOR, "#box > div.row.hero-section > div > div > article")
        
        title = ""
        tag = ""
        description = ""
        
        try:
            title = article.find_element(By.CSS_SELECTOR, "div div.av_img > h1").text.strip()
        except NoSuchElementException as e:
            print(f"Erreur lors de la récupération du titre : {e}")
            
        try:
            tag_element = article.find_element(By.CSS_SELECTOR, "div.fixed-post-info > div > div:nth-child(1)")
            tag = tag_element.text.strip()
        except NoSuchElementException as e:
            # Si l'élément tag n'est pas trouvé, laisser tag vide
            print("L'élément 'tag' n'a pas été trouvé.")
            
        try:
            description = " ".join([p.text.strip() for p in article.find_elements(By.CSS_SELECTOR, "p")])
        except Exception as e:
            print(f"Erreur lors de la récupération de la description : {e}")
        
        article_info = {
            "titre": title,
            "description": description,
            "date": date_format,
            "tag": tag,
            "source_link": "https://medias24.com/"
        }
        
        return article_info
    except Exception as e:
        print("Article introuvable :")
        
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#detail-article > div.section-detail")))
        article = driver.find_element(By.CSS_SELECTOR, "#detail-article > div.section-detail")
        
        title = ""
        tag = ""
        description1 = ""
        description2 = ""
        
        try:
            title = article.find_element(By.CSS_SELECTOR, "div.detail-title > h1").text.strip()
        except NoSuchElementException as e:
            print(f"Erreur lors de la récupération du titre : {e}")

        try:
            description1_element = article.find_element(By.CSS_SELECTOR, "div.description-article")
            description1 = description1_element.text.strip()
        except NoSuchElementException as e:
            print("L'élément 'description1' n'a pas été trouvé.")
            
        try:
            description2_elements = article.find_elements(By.CSS_SELECTOR, "div > p")
            description2 = " ".join([p.text.strip() for p in description2_elements])
        except NoSuchElementException as e:
            print("L'élément 'description2' n'a pas été trouvé.")

        # Concaténer les descriptions si elles ne sont pas vides
        if description1 and description2:
            article_info = {
                "titre": title,
                "description": f"{description1} {description2}",
                "date": date_format,
                "tag": tag,
                "source_link": "https://medias24.com/"
            }
        elif description1:
            article_info = {
                "titre": title,
                "description": description1,
                "date": date_format,
                "tag": tag,
                "source_link": "https://medias24.com/"
            }
        elif description2:
            article_info = {
                "titre": title,
                "description": description2,
                "date": date_format,
                "tag": tag,
                "source_link": "https://medias24.com/"
            }
        else:
            article_info = {
                "titre": title,
                "description": "",
                "date": date_format,
                "tag": tag,
                "source_link": "https://medias24.com/"
            }
        
        return article_info

    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des informations de l'article '{url}' : {e}")
        return None






def main20(date , driver):

 
    try:
        elements = date.split("-")
        date_format = f"{elements[2]}/{elements[1]}/{elements[0]}"
        news_list = []
        url = f"https://medias24.com/{date_format}"
        article_urls = get_article_urls(url, driver, 0)

        for i in tqdm(range(0,len(article_urls)), desc="Progression dans la url https://medias24.com/ "):
            try:
                article_info = get_article_info(article_urls[i], date_format, driver)
                if article_info is not None:
                    news_list.append(article_info)
            except Exception as e:
                print(f"Une erreur s'est produite lors du traitement de l'article '{url}': {e}")
       
        if os.path.isfile(f'{date}.xlsx'):
            existing_df = pd.read_excel(f'{date}.xlsx')
            if not news_list:
                print("La liste de nouvelles est vide. Aucune donnée n'a été ajoutée.")
            else:
                new_df = pd.DataFrame(news_list)
                df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            df = pd.DataFrame(news_list)

        if not df.empty:
            df = df[['titre', 'description', 'date', 'tag', 'source_link']]
            df.to_excel(f'{date}.xlsx', index=False)
            print(f"Les données ont été exportées avec succès vers '{date}.xlsx'.")
        else:
            print("Le DataFrame est vide. Aucun fichier Excel n'a été créé.")
        
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'exécution du programme  de https://medias24.com/: {e}")
        

