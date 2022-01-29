from utilitaires import *

config = {
    "fichier_climats": "climats_nb.png",
    "resolution_camera": (1376, 768),
    "duree_minutes": 1,
    "frequence_acquisition_secondes": 10,
    "dossier_enregistrement": "captures"
}

configure(config)

while not experience_terminee():
    temps = recuperer_temps()
    
    lumiere_du_jour = cote_jour(temps)
    lumiere_du_jour = True
    
    position = position_iss(temps)
    code_climat = recuperer_code_climat(position)
    
    donnees_a_sauvegarder = genere_infos_capture(temps, position, code_climat)
    
    if lumiere_du_jour:
        image = capture_image()
        image_traitee = traitement_image(image)
        nom_fichier_image = genere_nom_sauvegarde("capture", temps, "jpg")
        sauvegarde_image(image, nom_fichier_image)
        nom_fichier_image_traitee = genere_nom_sauvegarde("traitee", temps, "jpg")
        sauvegarde_image(image_traitee, nom_fichier_image_traitee)
        donnees_a_sauvegarder["capture"] = nom_fichier_image
        donnees_a_sauvegarder["traitement"] = nom_fichier_image_traitee
        print("Nombre 0:" + str(compte_nombre_indices(image_traitee, 0)))
        
    sauvegarde_infos_capture(donnees_a_sauvegarder, genere_nom_sauvegarde("donnees", temps, "json"))
        
    attendre(temps)