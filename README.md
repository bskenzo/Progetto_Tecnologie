![Movienet Logo](/static/img/Logofinale.png)

Movienet è un piattaforma di streaming online.

## **Raccomandazioni**

Per il corretto funzionamento del programma bisogna aver installato sul proprio pc [**python3.9**](https://www.python.org/downloads/)

## **Istallazione**

Per poter utilizzare **MOVIENET** è necessario installare i moduli Python necessari

1. Aprire una nuova finestra terminale
2. Entrare nella cartella del progetto
3. Lanciare i comandi di seguito elencati

Creazione di un ambiente virtuale:

```python
  pipenv shell
```

Istallazione dei requisiti necessari che sono contenuti nel Pipfile.lock con il comando:

```python
  pipenv install
```

Infine lanciare il programma con:

```python
  python manage.py runserver
```

Successivamente copiare ed incollare il seguente URL `https://127.0.0.1:8000/` su un Browser(consigliato l'uso di Google Chrome) ed il gioco è fatto!

## **Utenti**
Il progetto e fornito con:

  * Un utente amministratore
    *  Email: admin@gmail.com
    *  Password: admin

  * Un utente con abbonamento annuale
    * Email: abbonato@gmail.com
    * Password: prova1234

  * Un utente registrato
    * Email: toor@gmail.com
    * Password: prova1234

  * Un utente facente parte dello staff
    * Email: staff@gmail.com
    * Password: prova1234

E inoltre possibile creare altri utenti direttamente tramite app

## **Metodo di Pagamento**
Il metodo di pagamento è stato gestito tramite l'API esterna Stripe

Ai fini progettuali è stata attivata la modalità di test, è quindi possibile effettuare un pagamento inserendo i seguenti dati
* 4242 4242 4242 4242
* come data di scadenza e cvv è possibile inserire una qualsiasi data ancora in corso di validità e un qualsiasi cvv

## **Supporto**

Per ogni problema utilizzare i seguenti contatti:
* 243470@studenti.unimore.it - Davis Innangi
* 243895@studenti.unimore.it - Enzo Rotonda
