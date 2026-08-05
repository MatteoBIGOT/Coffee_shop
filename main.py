from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)
import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt


app = Flask(__name__)

load_dotenv()

app.secret_key = "cle-secrete-temporaire"


# ==================================================
# CONNEXION MYSQL
# ==================================================

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)


# ==================================================
# ACCUEIL
# ==================================================

@app.route("/")
def home():

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            products.id AS product_id,
            products.name AS product_name,
            categories.name AS category_name,
            products.price AS product_price,
            products.description AS product_description
        FROM products
        JOIN categories
            ON products.category_id = categories.id
        WHERE products.active = 1
    """)

    products = cursor.fetchall()

    cursor.close()

    print("ID :", session.get("user_id"))
    print("Username :", session.get("username"))
    print("Role :", session.get("role"))

    return render_template(
        "index.html",
        products=products
    )


# ==================================================
# INSCRIPTION
# ==================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor = db.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users
                (username, email, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    username,
                    email,
                    password_hash,
                    "client"
                )
            )

            db.commit()

        except mysql.connector.Error as error:

            db.rollback()

            cursor.close()

            return render_template(
                "register.html",
                error="Cette adresse email ou ce nom d'utilisateur existe déjà."
            )

        cursor.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ==================================================
# CONNEXION
# ==================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            """
            SELECT
                id,
                username,
                email,
                password,
                role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if user:

            password_hash = user["password"]

            if bcrypt.checkpw(
                password.encode("utf-8"),
                password_hash.encode("utf-8")
            ):

                print("Connexion réussie !")
                print("Utilisateur :", user["username"])
                print("Rôle :", user["role"])

                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]

                cursor.close()

                return redirect(url_for("home"))

            else:

                cursor.close()

                return render_template(
                    "login.html",
                    error="Mot de passe incorrect"
                )

        else:

            cursor.close()

            return render_template(
                "login.html",
                error="Utilisateur introuvable"
            )

    cursor.close()

    return render_template("login.html")


# ==================================================
# DECONNEXION
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ==================================================
# CREATION D'UNE COMMANDE
# ==================================================

@app.route("/orders", methods=["POST"])
def create_order():

    # Vérification de connexion
    user_id = session.get("user_id")

    if user_id is None:

        return {
            "error": "Vous devez être connecté pour commander."
        }, 401


    data = request.get_json()

    items = data["items"]


    cursor = db.cursor(dictionary=True)


    try:

        # ------------------------------------------
        # Création de la commande
        # ------------------------------------------

        cursor.execute(
            """
            INSERT INTO orders
            (user_id, state, price)
            VALUES (%s, %s, %s)
            """,
            (
                user_id,
                "pending",
                0
            )
        )

        order_id = cursor.lastrowid


        # ------------------------------------------
        # Ajout des produits
        # ------------------------------------------

        for item in items:

            product_id = item["product_id"]

            quantity = item["quantity"]


            cursor.execute(
                """
                SELECT price
                FROM products
                WHERE id = %s
                """,
                (product_id,)
            )

            result = cursor.fetchone()


            if result is None:

                raise Exception(
                    f"Produit {product_id} introuvable"
                )


            unit_price = result["price"]


            cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price
                )
            )


        # ------------------------------------------
        # Calcul du prix total
        # ------------------------------------------

        cursor.execute(
            """
            UPDATE orders
            SET price = (
                SELECT SUM(unit_price * quantity)
                FROM order_items
                WHERE order_id = %s
            )
            WHERE id = %s
            """,
            (
                order_id,
                order_id
            )
        )


        # ------------------------------------------
        # Validation de la transaction
        # ------------------------------------------

        db.commit()


    except Exception as error:

        # Annulation de toutes les requêtes
        db.rollback()

        cursor.close()

        print("Erreur commande :", error)

        return {
            "error": "Une erreur est survenue lors de la commande."
        }, 500


    cursor.close()


    return {
        "message": "Commande créée avec succès",
        "order_id": order_id
    }, 201


# ==================================================
# MES COMMANDES
# ==================================================

@app.route("/my-orders")
def my_orders():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "client":
        return redirect(url_for("seller"))

    user_id = session.get("user_id")


    # Utilisateur non connecté
    if user_id is None:

        return redirect(url_for("login"))


    cursor = db.cursor(dictionary=True)


    cursor.execute(
        """
        SELECT
            orders.id AS order_id,
            orders.state,
            orders.price,
            order_items.product_id,
            order_items.quantity,
            order_items.unit_price,
            products.name AS product_name
        FROM orders

        JOIN order_items
            ON orders.id = order_items.order_id

        JOIN products
            ON order_items.product_id = products.id

        WHERE orders.user_id = %s

        ORDER BY orders.id DESC
        """,
        (user_id,)
    )


    rows = cursor.fetchall()

    cursor.close()


    # ------------------------------------------
    # Regroupement des produits par commande
    # ------------------------------------------

    orders = {}


    for row in rows:

        order_id = row["order_id"]


        if order_id not in orders:

            orders[order_id] = {

                "order_id": order_id,

                "state": row["state"],

                "price": row["price"],

                "items": []

            }


        orders[order_id]["items"].append({

            "product_name": row["product_name"],

            "quantity": row["quantity"],

            "unit_price": row["unit_price"]

        })


    orders = list(orders.values())


    return render_template(
        "orders.html",
        orders=orders
    )

# ==================================================
# ESPACE VENDEUR
# ==================================================

@app.route("/seller")
def seller():

    # Vérification de connexion
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Vérification du rôle vendeur
    if session.get("role") != "seller":
        return redirect(url_for("home"))

    cursor = db.cursor(dictionary=True)

    try:

        # ==================================================
        # RÉCUPÉRATION DES COMMANDES
        # ==================================================

        cursor.execute("""
            SELECT
                orders.id AS order_id,
                orders.state,
                orders.price,
                users.username,
                order_items.product_id,
                order_items.quantity,
                order_items.unit_price,
                products.name AS product_name

            FROM orders

            JOIN users
                ON orders.user_id = users.id

            JOIN order_items
                ON orders.id = order_items.order_id

            JOIN products
                ON order_items.product_id = products.id

            WHERE orders.state != 'done'

            ORDER BY orders.id DESC
        """)

        rows = cursor.fetchall()


        # ==================================================
        # REGROUPEMENT DES PRODUITS PAR COMMANDE
        # ==================================================

        orders = {}

        for row in rows:

            order_id = row["order_id"]

            if order_id not in orders:

                orders[order_id] = {
                    "order_id": order_id,
                    "username": row["username"],
                    "state": row["state"],
                    "price": row["price"],
                    "items": []
                }


            orders[order_id]["items"].append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "quantity": row["quantity"],
                "unit_price": row["unit_price"]
            })


        # Conversion en liste pour Jinja
        orders = list(orders.values())


        # ==================================================
        # STATISTIQUES DES COMMANDES
        # ==================================================

        cursor.execute("""
            SELECT
                state,
                COUNT(*) AS total

            FROM orders

            WHERE state != 'done'

            GROUP BY state
        """)

        status_rows = cursor.fetchall()


        pending_count = 0
        preparing_count = 0
        ready_count = 0
        cancelled_count = 0


        for row in status_rows:

            if row["state"] == "pending":
                pending_count = row["total"]

            elif row["state"] == "preparing":
                preparing_count = row["total"]

            elif row["state"] == "ready":
                ready_count = row["total"]

            elif row["state"] == "cancelled":
                cancelled_count = row["total"]


        # ==================================================

        # RÉCUPÉRATION DES PRODUITS

        # ==================================================

        cursor.execute("""
            SELECT
            products.id,
            products.name,
            products.description,
            products.price,
            products.image,
            products.active,
            categories.name AS category_name

            FROM products

            LEFT JOIN categories
                ON products.category_id = categories.id

            ORDER BY products.name
        """)

        products = cursor.fetchall()


        # ==================================================
        # AFFICHAGE DU DASHBOARD
        # ==================================================

        return render_template(
            "seller.html",

            
            orders=orders,

            pending_count=pending_count,
            preparing_count=preparing_count,
            ready_count=ready_count,
            cancelled_count=cancelled_count,

            products=products
            

            )



    except mysql.connector.Error as error:

        print("Erreur dashboard vendeur :", error)

        return "Une erreur est survenue.", 500


    finally:

        cursor.close()
 
# ==================================================
# MODIFICATION DU STATUT D'UNE COMMANDE
# ==================================================

@app.route("/seller/order/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):

    # Vérification de connexion
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Vérification du rôle vendeur
    if session.get("role") != "seller":
        return redirect(url_for("home"))

    # Récupération du nouveau statut
    new_status = request.form["state"]

    # Statuts autorisés
    allowed_statuses = [
        "pending",
        "preparing",
        "ready",
        "done",
        "cancelled"
    ]

    # Vérification du statut
    if new_status not in allowed_statuses:
        return redirect(url_for("seller"))

    cursor = db.cursor()

    try:

        cursor.execute(
            """
            UPDATE orders
            SET state = %s
            WHERE id = %s
            """,
            (
                new_status,
                order_id
            )
        )

        db.commit()

    except mysql.connector.Error as error:

        db.rollback()

        print("Erreur modification statut :", error)

    finally:

        cursor.close()

    return redirect(url_for("seller"))

# ==================================================
# LANCEMENT
# ==================================================

@app.route("/add-product", methods=["GET", "POST"])
def add_product():

    # Vérification de connexion
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Seul un vendeur peut ajouter un produit
    if session.get("role") != "seller":
        return redirect(url_for("home"))


    cursor = db.cursor(dictionary=True)


    try:

        # ==================================================
        # RÉCUPÉRATION DES CATÉGORIES
        # ==================================================

        cursor.execute("""
            SELECT
                id,
                name

            FROM categories

            ORDER BY name
        """)

        categories = cursor.fetchall()


        # ==================================================
        # AFFICHAGE DU FORMULAIRE
        # ==================================================

        if request.method == "GET":

            return render_template(
                "add_product.html",
                categories=categories
            )


        # ==================================================
        # RÉCUPÉRATION DES DONNÉES
        # ==================================================

        name = request.form.get("name", "").strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        price = request.form.get(
            "price",
            ""
        ).strip()

        image = request.form.get(
            "image",
            ""
        ).strip()

        category_id = request.form.get(
            "category_id",
            ""
        ).strip()


        # ==================================================
        # VÉRIFICATION
        # ==================================================

        if not name:

            return render_template(
                "add_product.html",
                categories=categories,
                error="Le nom du produit est obligatoire."
            )


        if not price:

            return render_template(
                "add_product.html",
                categories=categories,
                error="Le prix est obligatoire."
            )


        if not category_id:

            return render_template(
                "add_product.html",
                categories=categories,
                error="Veuillez sélectionner une catégorie."
            )


        try:

            price = float(price)

            category_id = int(category_id)

        except ValueError:

            return render_template(
                "add_product.html",
                categories=categories,
                error="Le prix ou la catégorie est invalide."
            )


        if price < 0:

            return render_template(
                "add_product.html",
                categories=categories,
                error="Le prix ne peut pas être négatif."
            )


        # ==================================================
        # INSERTION DU PRODUIT
        # ==================================================

        cursor.execute("""
            INSERT INTO products
            (
                name,
                description,
                price,
                image,
                category_id
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            name,
            description,
            price,
            image if image else None,
            category_id
        ))


        db.commit()


        # Retour au dashboard vendeur
        return redirect(url_for("seller"))


    except mysql.connector.Error as error:

        db.rollback()

        print(
            "Erreur ajout produit :",
            error
        )

        return render_template(
            "add_product.html",
            categories=categories,
            error="Une erreur est survenue lors de l'ajout du produit."
        ), 500


    finally:

        cursor.close()

# =========================================================

# MODIFIER UN PRODUIT

# =========================================================

@app.route("/edit-product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

 
    # Vérification de connexion
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Seul un vendeur peut modifier les produits
    if session.get("role") != "seller":
        return redirect(url_for("home"))


    cursor = db.cursor(dictionary=True)


    try:

        # ==================================================
        # RÉCUPÉRATION DU PRODUIT
        # ==================================================

        cursor.execute("""
            SELECT
                id,
                name,
                description,
                price,
                image,
                category_id

            FROM products

            WHERE id = %s
        """, (product_id,))


        product = cursor.fetchone()


        # Produit inexistant
        if product is None:

            return "Produit introuvable", 404


        # ==================================================
        # RÉCUPÉRATION DES CATÉGORIES
        # ==================================================

        cursor.execute("""
            SELECT
                id,
                name

            FROM categories

            ORDER BY name
        """)


        categories = cursor.fetchall()


        # ==================================================
        # AFFICHAGE DU FORMULAIRE
        # ==================================================

        if request.method == "GET":

            return render_template(
                "edit_product.html",
                product=product,
                categories=categories
            )


        # ==================================================
        # RÉCUPÉRATION DES DONNÉES
        # ==================================================

        name = request.form.get(
            "name",
            ""
        ).strip()


        description = request.form.get(
            "description",
            ""
        ).strip()


        price = request.form.get(
            "price",
            ""
        ).strip()


        image = request.form.get(
            "image",
            ""
        ).strip()


        category_id = request.form.get(
            "category_id",
            ""
        ).strip()


        # ==================================================
        # VALIDATION
        # ==================================================

        if not name:

            return render_template(
                "edit_product.html",
                product=product,
                categories=categories,
                error="Le nom du produit est obligatoire."
            )


        if not price:

            return render_template(
                "edit_product.html",
                product=product,
                categories=categories,
                error="Le prix est obligatoire."
            )


        if not category_id:

            return render_template(
                "edit_product.html",
                product=product,
                categories=categories,
                error="Veuillez sélectionner une catégorie."
            )


        try:

            price = float(price)

            category_id = int(category_id)

        except ValueError:

            return render_template(
                "edit_product.html",
                product=product,
                categories=categories,
                error="Le prix ou la catégorie est invalide."
            )


        if price < 0:

            return render_template(
                "edit_product.html",
                product=product,
                categories=categories,
                error="Le prix ne peut pas être négatif."
            )


        # ==================================================
        # MODIFICATION
        # ==================================================

        cursor.execute("""
            UPDATE products

            SET
                name = %s,
                description = %s,
                price = %s,
                image = %s,
                category_id = %s

            WHERE id = %s
        """, (
            name,
            description,
            price,
            image if image else None,
            category_id,
            product_id
        ))


        db.commit()


        return redirect(url_for("seller"))


    except mysql.connector.Error as error:

        db.rollback()

        print(
            "Erreur modification produit :",
            error
        )

        return "Une erreur est survenue.", 500


    finally:

        cursor.close()
 

# =========================================================

# SUPPRIMER UN PRODUIT

# =========================================================

@app.route("/delete-product/<int:product_id>", methods=["POST"])
def delete_product(product_id):

    
    # Vérification de connexion
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Seul un vendeur peut supprimer
    if session.get("role") != "seller":
        return redirect(url_for("home"))


    cursor = db.cursor()


    try:

        cursor.execute("""
            DELETE FROM products

            WHERE id = %s
        """, (product_id,))


        db.commit()


        return redirect(url_for("seller"))


    except mysql.connector.Error as error:

        db.rollback()

        print(
            "Erreur suppression produit :",
            error
        )

        return "Impossible de supprimer ce produit.", 500


    finally:

        cursor.close()
 
@app.route("/toggle-product/<int:product_id>", methods=["POST"])
def toggle_product(product_id):
    # Vérification de connexion
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Seul un vendeur peut modifier les produits
    if session.get("role") != "seller":
        return redirect(url_for("home"))

    cursor = db.cursor()

    try:

        cursor.execute("""
            SELECT active
            FROM products
            WHERE id = %s
        """, (product_id,))

        product = cursor.fetchone()

        if product is None:
            return "Produit introuvable", 404

        new_state = 0 if product[0] else 1

        cursor.execute("""
            UPDATE products
            SET active = %s
            WHERE id = %s
        """, (
            new_state,
            product_id
        ))

        db.commit()

        return redirect(url_for("seller"))

    except mysql.connector.Error as error:

        db.rollback()

        print("Erreur changement disponibilité produit :", error)

        return "Impossible de modifier la disponibilité du produit.", 500

    finally:

        cursor.close()    

 
if __name__ == "__main__":

    app.run(debug=True)