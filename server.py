import json
from flask import Flask, render_template, request, redirect, flash, url_for

def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs

def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    club = next((club for club in clubs if club['email'] == request.form['email']), None)
    
    if not club:
        flash("Le club avec cet email n'existe pas.")
        return redirect(url_for('index'))

    return render_template('welcome.html', club=club, competitions=competitions)

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)

    if not foundClub or not foundCompetition:
        flash("Une erreur s'est produite - veuillez réessayer.")
        return redirect(url_for('showSummary'))

    return render_template('booking.html', club=foundClub, competition=foundCompetition)

@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)
    placesRequired = int(request.form['places'])

    # Vérification du nombre de places demandé
    if placesRequired < 1 or placesRequired > 12:
        flash("Le nombre de places doit être compris entre 1 et 12.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))

    # Vérification des points du club et des places disponibles pour la compétition
    if placesRequired > int(competition['numberOfPlaces']):
        flash(f"Erreur : Il ne reste que {competition['numberOfPlaces']} places disponibles.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))

    if placesRequired > int(club['points']):
        flash(f"Erreur : Vous n'avez que {club['points']} points disponibles.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))

    # Mise à jour du nombre de points du club et des places disponibles pour la compétition
    club['points'] = int(club['points']) - placesRequired
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    flash('Réservation réussie !')

    # PRG pattern pour éviter la soumission multiple en cas de rechargement de la page
    return redirect(url_for('showSummary'))

# TODO: Add route for points display

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()
