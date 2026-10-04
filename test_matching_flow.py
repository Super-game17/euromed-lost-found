from datetime import datetime

from app import create_app, db
from app.models import Claim, Item, User


app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    user = User(first_name="Test", last_name="User", email="test@example.com")
    user.set_password("secret")
    db.session.add(user)
    db.session.commit()

    lost_item = Item(
        user_id=user.id,
        item_type="lost",
        title="Portable perdu",
        category="Électronique",
        description="Portable noir",
        location="Bibliothèque",
        event_date=datetime(2025, 1, 10).date(),
        status="actif",
    )

    found_item = Item(
        user_id=user.id,
        item_type="found",
        title="Portable trouvé",
        category="Électronique",
        description="Portable noir",
        location="Bibliothèque",
        event_date=datetime(2025, 1, 12).date(),
        status="actif",
    )

    db.session.add_all([lost_item, found_item])
    db.session.commit()

    client = app.test_client()

    response = client.get(f"/matching/matches/{lost_item.id}")
    print("MATCH_PAGE_STATUS:", response.status_code)
    print("MATCH_FOUND:", "Portable trouvé" in response.get_data(as_text=True))
    print("CLAIM_LINK_PRESENT:", "Réclamer cet objet" in response.get_data(as_text=True))

    claim_response = client.post(
        f"/matching/claim/{found_item.id}",
        data={"proof_description": "Couleur noire, écran endommagé, coque bleue."},
        follow_redirects=True,
    )
    print("CLAIM_POST_STATUS:", claim_response.status_code)
    print("CLAIM_CREATED:", "Mes réclamations" in claim_response.get_data(as_text=True))

    claim = Claim.query.filter_by(item_id=found_item.id).first()
    print("CLAIM_ID:", claim.id if claim else None)
    print("CLAIM_STATUS:", claim.status if claim else None)

    manage_response = client.post(
        f"/matching/manage/{claim.id}",
        data={"action": "validate"},
        follow_redirects=True,
    )
    print("MANAGE_STATUS:", manage_response.status_code)
    print("MANAGE_VALIDATED:", "Réclamation" in manage_response.get_data(as_text=True))

    final_item = Item.query.get(found_item.id)
    print("ITEM_STATUS_AFTER_VALIDATE:", final_item.status)
