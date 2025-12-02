import csv
import time
from datetime import datetime
from contextlib import ExitStack

# --- Préparation : Création du fichier de données pour l'exercice ---
def creer_fichier_test(filename):
    donnees = [
        ["CMD001", "Traitement Image", "Haute"],
        ["CMD002", "Envoi Email", "Moyenne"],
        ["CMD003", "Erreur Attendue", "Critique"], # Servira au test d'erreur
        ["CMD004", "Sauvegarde BDD", "Basse"]
    ]
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Operation", "Priorite"])
        writer.writerows(donnees)

# --- Classe Gestionnaire de Contexte ---
class BatchProcessor:
    def __init__(self, csv_filename, log_filename):
        self.csv_filename = csv_filename
        self.log_filename = log_filename
        self._stack = ExitStack() # Gestionnaire de pile pour les fichiers
        self.reader = None
        self.log_file = None

    def __enter__(self):
        try:
            # On utilise le stack pour ouvrir les fichiers de manière sécurisée
            # Si l'ouverture du log échoue, le csv sera fermé automatiquement
            csv_file = self._stack.enter_context(open(self.csv_filename, 'r', newline='', encoding='utf-8'))
            self.log_file = self._stack.enter_context(open(self.log_filename, 'a', encoding='utf-8'))
            
            self.reader = csv.DictReader(csv_file)
            self._ecrire_log(f"DÉBUT du traitement du fichier {self.csv_filename}")
            
            return self
        except Exception as e:
            # En cas d'erreur lors de l'initialisation (__enter__), on nettoie
            self._stack.pop_all().close()
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cette méthode est appelée automatiquement à la fin du bloc with
        if exc_type:
            self._ecrire_log(f"ARRÊT D'URGENCE : Exception détectée -> {exc_val}")
        else:
            self._ecrire_log("FIN du traitement : Succès.")
        
        # Fermeture garantie de tous les fichiers ouverts via le stack
        self._stack.close()
        # Retourner False permet de propager l'exception pour qu'elle soit visible
        return False

    def _ecrire_log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_file.write(f"[{timestamp}] {message}\n")
        # Flush force l'écriture disque immédiate (utile pour le debug en temps réel)
        self.log_file.flush() 

    def traiter_commandes(self):
        print(f"--- Traitement lancé ---")
        for ligne in self.reader:
            op_id = ligne.get("ID")
            op_name = ligne.get("Operation")
            
            self._ecrire_log(f"Traitement de {op_id}: {op_name}")
            
            # Simulation de traitement
            time.sleep(0.5) 
            
            # Simulation d'une erreur critique sur une ligne spécifique
            if op_name == "Erreur Attendue":
                raise ValueError(f"Échec critique sur la commande {op_id}")
                
            print(f"   > {op_id} traité.")

# --- Exécution Principale ---
if __name__ == "__main__":
    fichier_csv = "operations.csv"
    fichier_log = "journal.log"
    
    # 1. Génération des données
    creer_fichier_test(fichier_csv)
    
    # 2. Utilisation du BatchProcessor
    print(f"Lancement du BatchProcessor sur {fichier_csv}...")
    
    try:
        with BatchProcessor(fichier_csv, fichier_log) as processor:
            processor.traiter_commandes()
            
    except ValueError as e:
        print(f"\n[Programme Principal] Une erreur est remontée du processeur : {e}")
    except FileNotFoundError:
        print("\n[Erreur] Le fichier d'entrée n'existe pas.")

    # 3. Vérification du fichier de log
    print(f"\n--- Contenu du fichier {fichier_log} ---")
    try:
        with open(fichier_log, 'r', encoding='utf-8') as f:
            print(f.read())
    except FileNotFoundError:
        print("Fichier log introuvable.")