# On dit à Python d'utiliser les fonctions du "module" random.
# Ces fonctions permettent de faire un tirage au sort d'une valeur.
# Si on ne fait pas ca, python ne saura pas faire de tirage au sort.
import random

# On définit une fonction, qui sera utilisée plus tard.
# "def" indique qu'on définit une fonction
# "verifie" est le nom qu'on lui donne
# "nombre_utilisateur" et "nombre_secret" correspondent aux 2 valeurs qu'on lui passe.
# Cette fonction vérifie si le nombre de l'utilisateur est égal, inférieur ou supérieur
# au nombre secret.
# En cas d'égalité (on a trouvé !), elle renvoie True (= OK, succès)
# Sinon elle renvoie False (= échec)
def verifie(nombre_utilisateur, nombre_secret):
    # Le contenu de la fonction commence ici, au moment où on se décale par rapport au début de la ligne
    
    # On teste d'abord si on a trouvé le nombre secret.
    # La comparaison d'égalité s'écrit == en python. Pas =, qui est utilisé pour autre chose.
    if nombre_utilisateur == nombre_secret:
        # Si on a trouvé le nombre secret, on écrit un message, on retourne True
        print("Vous avez trouvé !")
        return True # Fin de la fonction si on passe ici
    # Sinon, si notre nombre est trop petit, on l'écrit
    elif nombre_utilisateur < nombre_secret:
        print("Trop petit")
    # Sinon, c'est qu'il est trop grand
    else:
        print("Trop grand")
    
    # Si on est arrivé là, c'est qu'on n'est pas égal. Donc on renvoie false
    return False
    # Fin de la fonction

# En début de jeu, le nombre d'essais est nul.
# On met 0 dans la variable appelée compteur_d_essais.
# L'opérateur = sert à donner une valeur à une variable !
compteur_d_essais = 0
# On choisit un nombre au hasard entre 0 et 100, et on le place dans la variable nombre_a_trouver
nombre_a_trouver = random.choice(range(0, 100))
# En début de jeu, on n'a pas trouvé, on fait une variable appelee trouve, et on met False (faux)
trouve = False

# "while" signifie "tant que"
# "while not trouve" signifie tant que "not trouve" est vrai. "not trouve" est vrai quand trouve est faux (False).
# Donc l'instruction suivante dit "Tant qu'on n'a pas trouve, on va faire..."
while not trouve:
    # On demande à l'utilisateur une valeur, on la met dans nombre_teste_en_texte (on récupère un texte !)
    nombre_teste_en_texte = input("Entrez un nombre: ")
    # On convertit le texte en nombre entier ("integer" en anglais, abrégé en "int" en python)
    nombre_teste_en_valeur = int(nombre_teste_en_texte)
    # Et on appelle notre fonction "verifie", avec la valeur de l'utilisateur, et la valeur secrète
    # On met le résultat dans notre variable trouve
    trouve = verifie(nombre_teste_en_valeur, nombre_a_trouver)
    # On augment le compteur d'essais. On prend compteur_d_essais, on ajoute 1, et on remet dans compteur_d_essais
    compteur_d_essais = compteur_d_essais + 1
    # Fin du "tant que non trouve". Si trouve est False, on repart pour un tour, sinon on sort de la boucle.
    
# Et on affiche le résultat.
# str() permet de convertir le nombre compteur_d_essais en texte
print("Vous avez trouvé en " + str(compteur_d_essais) + " essais")

# Fin !
