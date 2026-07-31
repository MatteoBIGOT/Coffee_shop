const bouton = document.getElementById("btn");
const bouton2 = document.getElementById("btn2");

bouton.addEventListener("click", async () => {

    const reponse = await fetch("/bonjour");

    const data = await reponse.json();

    document.getElementById("texte").textContent = data.message;

});

bouton2.addEventListener("click", async () => {

    const reponse = await fetch("/test");

    const data = await reponse.json();

    document.getElementById("texte2").textContent = data.message;

});