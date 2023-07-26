from ..common import auth

auth.param.messages.update(
    
    task_failed = {
        "subject": "TASK FALLITO",
        "body": """Buongiorno {first_name},
Il task '{task_name}' (id: {task_id}) è fallito con il seguente errore:
========= Error =========
{trace_back}
=========================
Si prega di informare l'assistenza.
        """
    },

    task_success = {
        "subject": "TASK COMPLETATO CON SUCCESSO",
        "body": """Buongiorno {first_name},
Il task '{task_name}' (id: {task_id}) è statto completato.
========= Stats =========
Inizio elaborazione: {start_time}
Fine elaborazione: {end_time}
=========================
        """
    },

    mail_conf_check = {
        "subject": "Test cofigurazione mail",
        "body": """Configurazione di invio mail corretta"""
    }

)

def test_mail(recipient='manuele.pesenti@gter.it'):
    user = auth.db.auth_user(email=recipient)
    assert not user is None, "Utente richiesto per il test non esiste"
    success = auth.send('mail_conf_check', user)
    assert success
    return