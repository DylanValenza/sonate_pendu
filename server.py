from flask import Flask, render_template, request
import random, unicodedata

app = Flask(__name__)

#Variables utilitaires
lives = 0 #Variable stockant le nombre de vie
word = "" #Variable stockant le mot une fois pioché dans le dictionnaire
word_normalized = "" #Variable stockant une version du mot dite "normalisée. Cf "normalized_function".
hidden_word = [] #Liste de caractère stockant une version cachée de manière dynamique du mot.
game_status = 0 #Variable stockant le "statut" du jeu. 0 Le jeu n'a pas démarré. 1 Le jeu a démarré. 2 Le jeu est fini
player_name = "" #Variable stockant le nom du joueur.

#Fonctions utilitaires
#Cette fonction se charge de choisir un mot dans le dictionnaire
def choice_word():
    global word, player_name, word_normalized
    with open("dictionnaire.txt", "r", encoding="utf-8") as fichier:
        lines = fichier.readlines()     #Stocke les lignes du dictionnaire dans cette variable.
        pick_line = random.choice(lines)    #Choisis aléatoirement avec random une des lignes du dictionnaire.
        word = pick_line.strip().partition(";")[0]  #Stocke le mot dans une variable. Chaque ligne du dictionnaire a un pattern identique, j'ai donc isolé les caractères précédant le premier ";".
        word_normalized = normalized_function()     #Stocke dans une variable une version du mot dite "normalisée". Cf "normalized_function".

#Cette fonction s'occupe de créer une version normalisée, ne contenant pas de caractère avec accent. Lorsqu'un mot avec accent est pioché,
#lorsque le joueur clique sur un bouton, une fonction va comparer par exemple un "e" et un "é". Sans cette fonction, le jeu ne considère pas la,lettre trouvée
def normalized_function() :
    return ''.join( #On retourne le résultat directement dans la variable dans laquelle elle est stockée
        i2 for i2 in unicodedata.normalize('NFD', word) #Sépare les caractères de leur accents
        if unicodedata.category(i2) != 'Mn')    #Supprime ces caractères spéciaux

#Cette fonction s'occupe de la gestion de la variable qui va être affichée en jeu. Le mot indice demandé.
#Il créé une variable "mirroir" au mot pioché, cependant il va être masqué en jeu et être découverte peu à peu
#lorsque le joueur intéragit avec les différentes touches du clavier virtuel.
def hidden_word_management():
    global hidden_word, game_status, lives, hidden_word_final
    if game_status == 0 : #Le jeu n'a pas encore démarré
        hidden_word = list("_" * len(word)) #Créé une version cachée de la variable "word" avec le caractère "_" de la longueur de cette variable.
        game_status = 1 #Change le statut du jeu (dernière fonction utilisée dans la phase dite d'"initialisation", je pense qu'elle est bien placée pour cette raison.).
    else : #Donc dans le cas où le jeu a forcément déjà démarré
        if letter in word_normalized : #Dans le cas où la variable "letter" (donc la touche préssée par le joueur) est présente dans la verison normalisée du mot.
            for i1, char1 in enumerate(word_normalized) : #Va parcourir la version normalisée du mot au fur et à mesure
                if char1 == letter :    #Si la lettre actuellement lue est identique.
                    hidden_word[i1] = word[i1]  #Alors à l'index "i1", la lettre est placée dans la variable "hiden_word" et uniquement celle-ci. Cela permet aussi d'afficher les accents si tel est le cas. Dans l'exemple précédent, si le bouton "e" est pressé et qu'à cet endroit là c'est un "é", alors il l'affichera grâce a la variable "word" et à l'index "i1"
        else : #Si la lettre sélectionnée n'est pas présente
            lives -= 1  #Alors il retire un point de vie
    hidden_word_final = " ".join(hidden_word) #Cette variable stocke une version plus "esthetique", elle ajoute un espace entre tous les underscores/lettres trouvées dans la liste pour plus de lisibilité.

#Cette fonction "initialise" le jeu
def initialization() :
    global hidden_word_final, lives
    choice_word()
    hidden_word_management()
    lives = 5 #Attribue la valeur 5 car 5 points de vies sont demandés.

@app.route("/")
def home():
    global game_status
    game_status = 0 #Sécurise la variable en début de jeu.
    return render_template("home.html")

@app.route("/play", methods=["POST"])
def play():
    global game_status, player_name, letter, lives, hidden_word_final
    if game_status == 0 : #Rentre dans ce cas là uniquement en début de partie
        if request.method == "POST":
            player_name = request.form["player_name"] #Stocke le nom du joueur dans une variable afin de l'utiliser dans différentes pages.
        initialization()

    elif game_status == 1 : #Rentre dans ce cas là en cours de partie, lorsqu'une touche est pressée par exemple.
        letter = request.form["letter"].lower() #Stocke la lettre sélectionnée dans cette variable. Pour des raisons "esthétiques", les lettres affichées à l'écran sont en majuscules, par conséquent la valeur récupérée est en majuscule, il faut donc la stocker version minuscule.
        hidden_word_management()
        if lives == 0 : #Dans le cas où le nombre de vies tombe à 0.
            game_status = 2 #Attribue le statut de fin de partie.
            return render_template("gameover.html", player_name = player_name, word = word) #Rend la page de fin de partie version perdante.
        if word == "".join(hidden_word) : #Si ces deux variables sont identiques, c'est que le joueur a trouvé le mot. Particularité, on compare une chaine de caractère "word", et une liste de caractère "hidden_word". Cela permet de reconstruire une chaine sans espaces pour pouvoir comparer.
            game_status = 2 #Attribue le statut de fin de partie.
            return render_template("win.html", player_name = player_name, word = word)  #Rend la page de fin de partie version gagnante.
        
    elif game_status == 2 : #Rentre dans cette boucle uniquement lorsque la fin du jeu a été atteint et que le joueur veut réessayer.
        game_status = 0
        initialization()

    return render_template("play.html", player_name=player_name, hidden_word=hidden_word_final, lives=lives, word=word) #Se trouve en fin de fonction, car rend dans tous les cas la page "play" sauf dans les cas de fin de partie.