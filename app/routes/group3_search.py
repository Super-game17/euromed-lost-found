from flask import Blueprint, render_template, request
group3_search = Blueprint("group3_search", __name__)
# Données temporaires pour tester notre système.
# Elles seront remplacées par la base de données du projet
# lorsque le modèle Object du Groupe 2 sera validé.
OBJECTS = [
    {
        "id": 1,
        "type": "perdu",
        "titre": "Carte étudiant",
        "categorie": "Document",
        "description": "Carte étudiant perdue près de la bibliothèque",
        "date": "2026-09-22",
        "lieu": "Bibliothèque Euromed",
    },
    {
        "id": 2,
        "type": "trouvé",
        "titre": "Carte étudiant",
        "categorie": "Document",
        "description": "Carte étudiant trouvée près de la bibliothèque",
        "date": "2026-09-22",
        "lieu": "Bibliothèque Euromed",
    },
    {
        "id": 3,
        "type": "perdu",
        "titre": "Sac à dos noir",
        "categorie": "Sac",
        "description": "Sac à dos noir perdu dans le campus",
        "date": "2026-09-24",
        "lieu": "Campus Euromed",
    },
    {
        "id": 4,
        "type": "trouvé",
        "titre": "Clés",
        "categorie": "Clés",
        "description": "Trousseau de clés trouvé près du restaurant",
        "date": "2026-09-25",
        "lieu": "Restaurant universitaire",
    },
]
@group3_search.route("/search", methods=["GET"])
def search():
    # Récupération des critères envoyés par le formulaire
    keyword = request.args.get("keyword", "").strip().lower()
    category = request.args.get("category", "").strip()
    location = request.args.get("location", "").strip().lower()
    date = request.args.get("date", "").strip()
    object_type = request.args.get("type", "").strip()
    results = []
    for obj in OBJECTS:
        # Recherche par mot-clé
        if keyword:
            text = (
                obj["titre"]
                + " "
                + obj["description"]
                + " "
                + obj["categorie"]
                + " "
                + obj["lieu"]
            ).lower()
            if keyword not in text:
                continue
        # Filtre catégorie
        if category and obj["categorie"] != category:
            continue
        # Filtre lieu
        if location and location not in obj["lieu"].lower():
            continue
        # Filtre date
        if date and obj["date"] != date:
            continue
        # Filtre type : perdu / trouvé
        if object_type and obj["type"] != object_type:
            continue
        results.append(obj)
    return render_template(
        "group3/search.html",
        results=results,
        keyword=keyword,
        category=category,
        location=location,
        date=date,
        object_type=object_type,
    )
@group3_search.route("/object/<int:object_id>")
def details(object_id):
    for obj in OBJECTS:
        if obj["id"] == object_id:
            return f"""
                <h1>{obj["titre"]}</h1>
                <p>Type : {obj["type"]}</p>
                <p>Catégorie : {obj["categorie"]}</p>
                <p>Description : {obj["description"]}</p>
                <p>Date : {obj["date"]}</p>
                <p>Lieu : {obj["lieu"]}</p>
            """
    return "Objet introuvable", 404