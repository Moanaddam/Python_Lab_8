from contextlib import ExitStack
from datetime import datetime

class ConnectionManager:
    def __init__(self, service_name):
        self.service_name = service_name

    def __enter__(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Connexion à {self.service_name} établie.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Déconnexion de {self.service_name}.")
        if exc_type:
            print(f"Erreur détectée : {exc_type.__name__} — {exc_value}")

if __name__ == "__main__":
    print("--- SCÉNARIO 1 : Succès ---")
    try:
        with ExitStack() as stack:
            log_file = stack.enter_context(open("log_activite.txt", "a", encoding="utf-8"))
            conn = stack.enter_context(ConnectionManager("Serveur_Production"))
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"[{timestamp}] Tâche effectuée sur {conn.service_name}\n")
            print("Action terminée avec succès.")

    except Exception as e:
        print(f"Erreur externe : {e}")

    print("\n--- SCÉNARIO 2 : Simulation d'Erreur ---")
    try:
        with ExitStack() as stack:
            log = stack.enter_context(open("log_erreur.txt", "a", encoding="utf-8"))
            conn = stack.enter_context(ConnectionManager("Base_SQL_Legacy"))
            
            raise RuntimeError("Échec critique du traitement")

    except RuntimeError as e:
        print(f"Exception remontée au programme principal : {e}")

    print("\n--- SCÉNARIO 3 : Connexions Multiples ---")
    services = ["API_Auth", "API_Payment", "API_Notification"]
    
    with ExitStack() as stack:
        conns = [stack.enter_context(ConnectionManager(svc)) for svc in services]
        print("Traitement global en cours...")