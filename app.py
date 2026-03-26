import pymysql
from flask import Flask, render_template ,request
from database import get_connection

app = Flask(__name__)

@app.route('/')
def index():
    requete=("SELECT * FROM logs_acces "
             "WHERE TIMEDIFF(NOW(), horodatage) < '24:00:00' AND acces_autorise=0 "
             "ORDER BY horodatage DESC "
             "LIMIT 10")
    co = get_connection()
    curseur = co.cursor()
    curseur.execute(requete)
    logs = curseur.fetchall()
    nbrLogs = curseur.rowcount
    curseur.close()
    co.close()
    print("NBR ACCES 24H: ", nbrLogs)
    print(logs)
    return render_template('index.html', logs=logs, nbrLogs=nbrLogs)

#*****************************************************************************************
@app.route("/testBdd")
def accueil():
    co = get_connection()
    if co:
        co.close()
        return "Connexion MySQL réussie"
    else:
        return "Erreur de connexion MySQL"

#*****************************************************************************************
@app.route('/affichage_logs')
def affichage_logs():
    co=get_connection()
    curseur = co.cursor()
    requete_sql = "SELECT * FROM logs_acces ORDER BY horodatage DESC "
    curseur.execute(requete_sql)
    logs = curseur.fetchall()
    curseur.close()
    co.close()
    print(logs)
    return render_template('affichage_logs.html', logs=logs)

#*****************************************************************************************

@app.route("/delete")
def delete():
    id_user=1
    co = get_connection()
    curseur = co.cursor()
    requete = "DELETE FROM users WHERE id = %s"
    curseur.execute(requete, id_user)
    co.commit()
    print(curseur.rowcount, "ligne supprimée")
    curseur.close()
    co.close()
    return "Suppression terminée"



@app.route("/ajouter_utilisateur", methods=["GET", "POST"])
def ajouter_utilisateur():
    if request.method == "POST":
        prenom = request.form["prenom"]
        nom = request.form["nom"]
        code_carte = request.form["code_carte"]
        activation_carte = request.form["activation_carte"]
        acces_bureau = request.form["acces_bureau"]
        acces_stock = request.form["acces_stock"]
        acces_informatique = request.form["acces_info"]
        acces_technique = request.form["acces_technique"]

        print(prenom, nom, code_carte, activation_carte, acces_bureau, acces_stock, acces_informatique,acces_technique)

        co = get_connection()
        curseur = co.cursor()
        requete = """
            INSERT INTO users (prenom, nom, code_carte,carte_active, z_bureaux, z_stock, z_info, z_technique) 
            VALUES (%s, %s, %s, %s, %s,%s, %s, %s)
        """
        curseur.execute(requete, (prenom, nom, code_carte,activation_carte,acces_bureau,acces_stock,acces_informatique,acces_technique))
        co.commit()
        nb = curseur.rowcount
        curseur.close()
        co.close()
        return render_template("info_retour.html", res=f"{nb} utilisateur ajouté")

    return render_template("ajouter_utilisateur.html")

@app.route("/demande_autorisation", methods=["POST"])
def demande_autorisation():
    #print("Headers:", request.headers)
    #print("Raw data:", request.get_data())
    #print("Form:", request.form)
    uid = request.form['uid']
    zone = request.form['zone']
    auth=1
    print("****** Parametres reçus du lecteur de badge: zone=",zone,"uid=",uid,"******")
    co = get_connection()
    if co:
        curseur = co.cursor()
        requete = (f"SELECT * FROM `users_zones` "
                   f"INNER JOIN users ON users_zones.id_user=users.id "
                   f"WHERE users.code_carte=%s AND users_zones.id_zone=%s")
        curseur.execute(requete, (uid, zone))
        reponse = curseur.fetchone()
        print("Reponse de la Bdd:", reponse)
        requete = ("INSERT INTO logs_acces (id_user, id_zone, acces_autorise) "
                   "SELECT users.id, users_zones.id_zone, %s FROM users "
                   "INNER JOIN users_zones ON users.id=users_zones.id_user "
                   "WHERE users.code_carte=%s AND users_zones.id_zone=%s")

        if reponse==None:
            auth=0
            requete = ("INSERT INTO logs_acces (id_user, id_zone, acces_autorise) "
                       "SELECT users.id, %s, %s FROM users "
                       "WHERE users.code_carte=%s "
                       "LIMIT 1")
            curseur.execute(requete, (zone, auth, uid))
            co.commit()
            print(curseur.rowcount, curseur.fetchall())
            curseur.close()
            co.close()
            reponseJson = {"nom": uid, "zone": zone, "autorisation": 0}
            return reponseJson
        curseur.execute(requete, (auth, reponse['code_carte'], zone))
        co.commit()
        print(curseur.rowcount, curseur.fetchall())
        curseur.close()
        co.close()


        reponseJson = {"nom": reponse['nom'], "zone": zone, "autorisation":1}
        print(reponseJson)
        return reponseJson

    else:
        return "Erreur Bdd"
@app.route("/update", methods=["POST"])
def update():
    global last_measure
    data_requetePost = request.data.decode("utf-8")
    print("Nouvelle demande:", data_requetePost)
    return "OK"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)