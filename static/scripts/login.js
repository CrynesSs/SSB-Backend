let userPublicKeyPem = null;

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("publicKeyFile").addEventListener("change", async function () {
        const file = this.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (event) {
            userPublicKeyPem = event.target.result;
            localStorage.setItem("salt_pubkey_pem", userPublicKeyPem);
            console.log("Public key loaded");
        };
        reader.readAsText(file);
    });
    document.getElementById("login-form").addEventListener("submit", async (e) => {
        e.preventDefault();

        if (!userPublicKeyPem) {
            alert("Please upload your public key first.");
            return;
        }
        fetch("/login", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: await setupRequestBody()
        })
            .then(r => {
                if (r.ok) {
                    window.location.href = "/accounts/dashboard"
                }
            })
            .catch(reason => {
                console.log(reason)
            });

    });
    document.getElementById("signup-button").addEventListener("click", async (e) => {
        e.preventDefault();

        fetch("/accounts/create_account", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: await setupRequestBody()
        })
            .then(r => r.json()).then(console.log)
            .catch(reason => {
                console.log(reason)
            });
    })
})

function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    const binary = bytes.reduce((acc, byte) => acc + String.fromCharCode(byte), '');
    return btoa(binary);
}

async function setupRequestBody() {
    if (!userPublicKeyPem) {
        alert("Please upload your public key first.");
        return;
    }
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const passphrase = document.getElementById("passphrase").value;

    const hashedUsername = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(username));
    const hashedPassword = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(password));
    const hashedPassphrase = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(passphrase));

    const encryptedUsername = arrayBufferToBase64(hashedUsername);
    const encryptedPassword = arrayBufferToBase64(hashedPassword);
    const encryptedPassphrase = arrayBufferToBase64(hashedPassphrase);

    return JSON.stringify({
        username: encryptedUsername,
        password: encryptedPassword,
        passphrase: encryptedPassphrase,
        public_key: userPublicKeyPem
    });
}

