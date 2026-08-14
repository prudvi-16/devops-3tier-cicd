const BACKEND_URL = "http://" + window.location.hostname + ":8080";

async function checkBackend() {
    const responseBox = document.getElementById("response");

    responseBox.innerText = "Checking backend...";

    try {
        const response = await fetch(BACKEND_URL + "/api");

        if (!response.ok) {
            throw new Error("Backend returned an error");
        }

        const data = await response.json();

        responseBox.innerText = data.message;
    } catch (error) {
        responseBox.innerText = "Backend connection failed";
        console.error(error);
    }
}

window.onload = checkBackend;
