/*

 
PANIER
 

====================================================
*/

let cart = [];

 /*

 
RÉCUPÉRATION DES ÉLÉMENTS HTML
 

====================================================
*/

const addButtons = document.querySelectorAll(".add-button");

const cartElement = document.getElementById("cart");

const cartButton = document.getElementById("cart-button");

const closeCartButton = document.getElementById("close-cart");

const cartItemsElement = document.getElementById("cart-items");

const cartCountElement = document.getElementById("cart-count");

const cartTotalElement = document.getElementById("cart-total");

const orderButton = document.getElementById("order-button");

/*

 
AJOUTER UN PRODUIT AU PANIER
 

====================================================
*/

addButtons.forEach(button => {

 
button.addEventListener("click", () => {

    const productId = Number(button.dataset.productId);

    const productName = button.dataset.productName;

    const productPrice = Number(button.dataset.productPrice);


    // Vérifier si le produit existe déjà dans le panier

    const existingProduct = cart.find(
        item => item.product_id === productId
    );


    if (existingProduct) {

        // Le produit existe déjà
        // On augmente simplement sa quantité

        existingProduct.quantity++;

    } else {

        // Nouveau produit

        cart.push({
            product_id: productId,
            product_name: productName,
            price: productPrice,
            quantity: 1
        });

    }


    updateCart();

});
 

});

/*

 
METTRE À JOUR LE PANIER
 

====================================================
*/

function updateCart() {

 
cartItemsElement.innerHTML = "";


let total = 0;

let numberOfProducts = 0;


/*
--------------------------------------------
    PANIER VIDE
--------------------------------------------
*/

if (cart.length === 0) {

    cartItemsElement.innerHTML = `
        <p>Votre panier est vide.</p>
    `;

}


/*
--------------------------------------------
    AFFICHAGE DES PRODUITS
--------------------------------------------
*/

cart.forEach(item => {

    const lineTotal = item.price * item.quantity;


    total += lineTotal;

    numberOfProducts += item.quantity;


    const cartItem = document.createElement("div");

    cartItem.classList.add("cart-item");


    cartItem.innerHTML = `

        <div class="cart-item-info">

            <strong>
                ${item.product_name}
            </strong>

            <p>
                ${item.price.toFixed(2)} €
                ×
                ${item.quantity}
            </p>

        </div>


        <strong>
            ${lineTotal.toFixed(2)} €
        </strong>

    `;


    cartItemsElement.appendChild(cartItem);

});


/*
--------------------------------------------
    TOTAL
--------------------------------------------
*/

cartCountElement.textContent = numberOfProducts;

cartTotalElement.textContent =
    total.toFixed(2) + " €";
 

}

/*

 
OUVRIR LE PANIER
 

====================================================
*/

cartButton.addEventListener("click", () => {

 
cartElement.classList.add("open");
 

});

 /*

 
FERMER LE PANIER
 

====================================================
*/

closeCartButton.addEventListener("click", () => {

 
cartElement.classList.remove("open");
 

});

 /*

 
PASSER LA COMMANDE
 

====================================================
*/

orderButton.addEventListener("click", async () => {

 
/*
--------------------------------------------
    Vérifier que le panier n'est pas vide
--------------------------------------------
*/

if (cart.length === 0) {

    alert("Votre panier est vide.");

    return;

}


/*
--------------------------------------------
    Préparer les données pour Flask
--------------------------------------------

    IMPORTANT :

    On n'envoie PAS :

    - user_id
    - price
    - unit_price

    Flask récupère lui-même le user_id
    depuis la session et les prix depuis MySQL.
--------------------------------------------
*/

const items = cart.map(item => {

    return {
        product_id: item.product_id,
        quantity: item.quantity
    };

});


try {


    /*
    ----------------------------------------
        ENVOI À FLASK
    ----------------------------------------
    */

    const response = await fetch("/orders", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            items: items
        })

    });


    /*
    ----------------------------------------
        RÉCUPÉRATION DE LA RÉPONSE
    ----------------------------------------
    */

    const result = await response.json();


    /*
    ----------------------------------------
        COMMANDE CRÉÉE
    ----------------------------------------
    */

    if (response.ok) {

        alert(
            "Commande créée !\n" +
            "Numéro : " +
            result.order_id
        );


        // Vider le panier

        cart = [];

        updateCart();


        // Fermer le panier

        cartElement.classList.remove("open");


    } else {


        /*
        ------------------------------------
            ERREUR FLASK
        ------------------------------------
        */

        alert(
            "Erreur : " +
            (result.error || "Une erreur est survenue.")
        );

    }


} catch (error) {


    /*
    ----------------------------------------
        SERVEUR INACCESSIBLE
    ----------------------------------------
    */

    console.error(
        "Erreur lors de l'envoi de la commande :",
        error
    );


    alert(
        "Impossible de contacter le serveur."
    );

}
 

});

 /*

 
INITIALISATION
 

====================================================
*/

updateCart();
