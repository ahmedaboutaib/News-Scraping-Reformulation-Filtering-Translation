import schedule
import time
from selenium import webdriver
from tqdm import tqdm
from script1_selenium  import main1
from script2_selenium import main2
from script3_selenuim import main3
from script4_selenium import main4
from script5_selenium import main5
from script6_selenium import main6
from script7_selenuim import main7
from script8_selenium import main8
from script9_selenium import main9
from script10_selenium import main10
from script11_selenium import main11
from script12_selenium import main12
from script13_selenium import main13
from script14_selenium import main14
from script15_selenium import main15
from script16_selenium import main16
from script17_selenium import main17
from script18_selenuim import main18
from script19_selenium import main19
from script20_selenium import main20
from googledrive import googleDriver
import pendulum

from googledrive import supp
from filtrage import filtre
from reformulation import traiter_fichier_excel

def job():
    '''
    geckodriver_path = "/usr/bin/geckodriver"
 
    # Configuration du pilote Firefox avec les options
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options) '''
    # Utilisation de Firefox en mode headless
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)

    try:
        functions = [
            (main1, "https://detafour.ma/"),
            (main2, "https://fr.le360.ma/"),
            (main3, "https://www.lesiteinfo.com/"),
            (main4, "https://lematin.ma/"),
            (main5, "https://www.lemonde.fr/maroc/"),
            (main6, "https://www.maroc-hebdo.press.ma/"),
            (main7, "https://leseco.ma/"),
            (main8, "https://telquel.ma/"),
            (main9, "https://www.lopinion.ma/"),
            (main10, "https://www.leconomiste.com/"),
            (main11, "https://www.lepoint.fr/tags/maroc "),
            (main12, "https://www.cg.gov.ma/fr/communiques-de-presse"),
            (main13, "https://www.finances.gov.ma/fr/Pages/actualites.aspx"),
            (main14, "https://www.hcp.ma/"),
            (main15, "https://perspectivesmed.com/"),
            (main16, "https://www.hespress.com/"),
            (main17, "https://www.bladi.net/maroc.html"),
            (main18, "https://chantiersdumaroc.ma"),
            (main19, "https://aujourdhui.ma"),
            (main20, "https://medias24.com/"),
        ]
        
        # Obtenir la date actuelle moins un jour
        date_obj = pendulum.now().subtract(days=1)
        date_minus_one_day = date_obj.format("DD-MM-YYYY")
        print(date_minus_one_day)

        for func, desc in functions:
            tqdm(func(date_minus_one_day, driver), desc=f"Progression dans la url {desc}")
        
        input_fil = f'{date_minus_one_day}.xlsx'
        input_ref = f'filtre-{date}.xlsx'
        output_ref = f'{date_minus_one_day}-final.xlsx'
        filtre(input_fil)
        traiter_fichier_excel(input_ref,output_ref)
        supp(input_fil)
        supp(input_ref)
        destination_folder_id = "1yE0k2DherUVaGBm7g0oNwmE-J3HyYipe"
        googleDriver(destination_folder_id,date_minus_one_day)

    finally:
        driver.quit()



if __name__ == "__main__":
    # Définir l'heure d'exécution
    schedule.every().day.at("00:02").do(job)

    while True:
        schedule.run_pending()
        time.sleep(60) 
        # Attendre 60 secondes avant de vérifier à nouveau
