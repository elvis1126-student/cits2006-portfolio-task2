console.log("JS loaded");

// Use explicit backend URL (prevents common bugs)
const API = "http://127.0.0.1:5000";

// ------------------ LOGIN ------------------
function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    console.log("Attempt login:", username);

    fetch(API + "/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ username, password })
    })
    .then(res => {
        console.log("HTTP status:", res.status);
        return res.json();
    })
    .then(data => {
        console.log("Response:", data);

        if (data.status === "success") {
            console.log("Login success → redirecting...");
            window.location.href = "/dashboard";
        } else {
            
            window.location.href = "/login_page";
            console.log("Invalid username or password");
            
        }
    })
    .catch(err => {
        console.error("Login error:", err);
        alert("Server error");
    });
}


// ------------------ COMMENTS ------------------
function sendComment() {
    const input = document.getElementById("comment");
    const comment = input.value;

    if (!comment.trim()) return;

    fetch(API + "/comment", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ comment })
    })
    .then(res => res.json())
    .then(data => {
        console.log("Saved:", data);
        input.value = "";
        loadComments();
    })
    .catch(err => console.error("Comment error:", err));
}


function loadComments() {
    fetch(API + "/comments")
    .then(res => {
        if (!res.ok) throw new Error("Failed to fetch comments");
        return res.json();
    })
    .then(data => {
        const container = document.getElementById("comments");
        if (!container) return;

        let html = "";
        data.forEach(c => {
            html += `<p>${c}</p>`; // intentionally vulnerable (XSS lab)
        });

        container.innerHTML = html;
    })
    .catch(err => console.error("Load error:", err));
}


// ------------------ AUTO LOAD ------------------
window.onload = () => {
    console.log("Page loaded");

    if (document.getElementById("comments")) {
        loadComments();
    }
};


// ------------------ CACHE FIX ------------------
window.onpageshow = function (event) {
    if (event.persisted || performance.getEntriesByType("navigation")[0]?.type === "back_forward") {
        window.location.reload();
    }
};