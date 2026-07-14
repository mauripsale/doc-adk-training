from unittest.mock import MagicMock, patch
import pytest
from app.tools import salva_qualificazione

@pytest.fixture
def mock_firestore_db():
    """
    Fixture che fa il mock del client Firestore e dei suoi metodi.
    """
    with patch('app.tools.db') as mock_db:
        # Crea mock per le varie concatenazioni: db.collection().document().set()
        mock_collection = MagicMock()
        mock_document = MagicMock()

        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document

        yield mock_db, mock_collection, mock_document

def test_salva_qualificazione_restituisce_stringa_corretta(mock_firestore_db):
    """
    Verifica che il tool restituisca la stringa formattata correttamente per Firestore.
    """
    _, _, mock_document = mock_firestore_db

    # Simula un salvataggio con successo
    mock_document.set.return_value = None

    risultato = salva_qualificazione("Azienda Test", "Descrizione Test", "competitor", 50)
    assert risultato == "Qualificazione salvata con successo per Azienda Test su Firestore: competitor con volume 50."

def test_salva_qualificazione_inserisce_dati_firestore(mock_firestore_db):
    """
    Verifica che il tool chiami correttamente collection, document e set con i dati giusti.
    """
    mock_db, mock_collection, mock_document = mock_firestore_db

    salva_qualificazione("Azienda Bio", "Produce bio", "storico", 20)

    # Controlliamo che sia stata chiamata la collection giusta
    mock_db.collection.assert_called_once_with("qualificazioni")

    # Controlliamo che document() sia stato chiamato
    mock_collection.document.assert_called_once()

    # Controlliamo che set sia stato chiamato con il dizionario corretto
    args, _ = mock_document.set.call_args
    assert len(args) == 1

    dati_salvati = args[0]
    assert dati_salvati["nome_azienda"] == "Azienda Bio"
    assert dati_salvati["descrizione_azienda"] == "Produce bio"
    assert dati_salvati["tipo"] == "storico"
    assert dati_salvati["volume"] == 20
    assert "timestamp" in dati_salvati

def test_salva_qualificazione_gestisce_errori(mock_firestore_db):
    """
    Verifica che il tool gestisca correttamente le eccezioni restituendo l'errore formattato.
    """
    _, _, mock_document = mock_firestore_db

    # Simula un errore durante il salvataggio
    mock_document.set.side_effect = Exception("Permessi insufficienti")

    risultato = salva_qualificazione("Azienda Errore", "Desc", "proxy", 10)
    assert "Errore durante il salvataggio su Firestore: Permessi insufficienti" in risultato
