from pathlib import Path
from contextlib import contextmanager, ExitStack
import time

# --- Partie 1 : Gestion manuelle (Classe) avec Logs et Gestion d'Erreur ---
class TempFileWriter:
    def __init__(self, filename):
        self.filepath = Path(filename)
        self.f = None

    def __enter__(self):
        print(f"[LOG] Création et ouverture du fichier : {self.filepath}")
        self.f = self.filepath.open("w", encoding="utf-8")
        return self.f

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Fermeture du fichier
        if self.f:
            self.f.close()
        
        # Suppression du fichier (Nettoyage)
        if self.filepath.exists():
            print(f"[LOG] Suppression du fichier temporaire : {self.filepath}")
            self.filepath.unlink()
        
        # Gestion de la reprise sur exception
        if exc_type:
            print(f"[ALERTE] Une exception a été capturée : {exc_val}")
            # Retourner True empêche l'arrêt du programme (l'erreur est "absorbée")
            return True 

# --- Partie 2 : Gestion via Générateur (contextlib) avec Logs ---
@contextmanager
def temp_file_generator(filename):
    path = Path(filename)
    print(f"[LOG-GEN] Ouverture {filename}")
    f = path.open("w", encoding="utf-8")
    try:
        yield f
    except Exception as e:
        print(f"[LOG-GEN] Erreur détectée dans le bloc : {e}")
        raise e  # On relance l'erreur après l'avoir loguée
    finally:
        # Ce bloc s'exécute toujours, erreur ou pas
        print(f"[LOG-GEN] Fermeture et nettoyage {filename}")
        f.close()
        if path.exists():
            path.unlink()

# --- Extension : Simulation Connexion Base de Données ---
class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        print(f"[DB] Connexion à {self.db_name} établie.")
        return self

    def query(self, sql):
        print(f"[DB] Exécution SQL : {sql}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[DB] Connexion à {self.db_name} fermée.")

# --- Exécution Principale ---
if __name__ == "__main__":
    
    # 1. Test de la classe (Partie 1)
    print("--- 1. Test TempFileWriter (Classe) ---")
    with TempFileWriter("temp_class.txt") as f:
        f.write("Test avec la classe\n")
        # Simulation d'une erreur pour tester le __exit__
        # raise ValueError("Oups, une erreur volontaire !") 

    

    # 2. Test du générateur (Partie 2)
    print("\n--- 2. Test temp_file_generator (Décorateur) ---")
    with temp_file_generator("temp_gen.txt") as f:
        f.write("Test avec le générateur\n")

    # 3. Test ExitStack pour multiples ressources (Partie 3)
    print("\n--- 3. Test ExitStack (Multi-fichiers) ---")
    fichiers = ["log_a.txt", "log_b.txt", "log_c.txt"]
    
    with ExitStack() as stack:
        # Ouverture dynamique de plusieurs fichiers
        files_handles = [
            stack.enter_context(open(p, "w", encoding="utf-8")) 
            for p in fichiers
        ]
        
        print(f"[STACK] {len(files_handles)} fichiers ouverts simultanément.")
        for f in files_handles:
            f.write("Donnée partagée\n")
    
    # Nettoyage manuel pour l'exercice (car ExitStack ferme mais ne supprime pas ici)
    print("[STACK] Nettoyage des fichiers de test...")
    for p in fichiers:
        Path(p).unlink(missing_ok=True)

    # 4. Extension : Base de données
    print("\n--- 4. Extension : Connexion Simulée ---")
    with DatabaseConnection("UserDB") as db:
        db.query("SELECT * FROM users")