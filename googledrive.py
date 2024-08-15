from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import pendulum

# Obtenir la date actuelle moins un jour
date_obj = pendulum.now().subtract(days=2)
date_minus_one_day2 = date_obj.format("DD-MM-YYYY")
print(date_minus_one_day2)


def supp(chemin_fichier_excel):
    
    if os.path.exists(chemin_fichier_excel):
        os.remove(chemin_fichier_excel)
        print("Le fichier Excel a été supprimé avec succès.")
    else:
        print("Le fichier spécifié n'existe pas.")
        
# Authentification Google Drive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Fonction pour envoyer le fichier Excel vers Google Drive
def googleDriver(destination_folder_id, date):
    # Vérification de l'existence du fichier Excel local
    chemin_fichier_excel = f"{date}.xlsx"
    if not os.path.exists(chemin_fichier_excel):
        print(f"Le fichier Excel {chemin_fichier_excel} n'existe pas.")
        return

    # Création de l'objet GoogleDriveFile pour le fichier Excel
    fichier_excel = drive.CreateFile({'title': f'{date}.xlsx',
                                      'parents': [{'id': destination_folder_id}]})
    # Paramétrage du contenu du fichier
    fichier_excel.SetContentFile(chemin_fichier_excel)

    # Tentative d'envoi du fichier vers Google Drive
    try:
        fichier_excel.Upload()
        print("Fichier Excel envoyé avec succès vers Google Drive.")
        # Suppression du fichier local après un envoi réussi
        
    except Exception as e:
        # Gestion des erreurs
        print(f"Erreur : {str(e)}")

