const API_URL = "https://watch-api-eight.vercel.app";
const API_KEY = "watch-api-001";

const requestHeaders = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
};

// Redirect if already logged in
if (localStorage.getItem("watch_user")) {
    window.location.href = "index.html";
}

let isRegisterMode = false;

const authForm = document.getElementById("authForm");
const authFormTitle = document.getElementById("authFormTitle");
const authSubtitle = document.getElementById("authSubtitle");
const authSubmitBtn = document.getElementById("authSubmitBtn");
const guestLoginBtn = document.getElementById("guestLoginBtn");
const switchPrompt = document.getElementById("switchPrompt");
const switchModeBtn = document.getElementById("switchModeBtn");
const authMessage = document.getElementById("authMessage");

// Continue as Guest
guestLoginBtn.addEventListener("click", () => {
    localStorage.setItem("watch_user", JSON.stringify({ username: "Guest", role: "guest" }));
    window.location.href = "index.html";
});

// Toggle between Login and Register
switchModeBtn.addEventListener("click", () => {
    isRegisterMode = !isRegisterMode;
    authMessage.textContent = "";
    authMessage.className = "auth-message";

    if (isRegisterMode) {
        authFormTitle.textContent = "Create Account";
        authSubtitle.textContent = "Create an account to view the full collection.";
        authSubmitBtn.textContent = "CREATE ACCOUNT";
        switchPrompt.textContent = "Already have an account?";
        switchModeBtn.textContent = "Sign In";
    } else {
        authFormTitle.textContent = "Sign In";
        authSubtitle.textContent = "Enter your account details below.";
        authSubmitBtn.textContent = "SIGN IN";
        switchPrompt.textContent = "Don't have an account?";
        switchModeBtn.textContent = "Create Account";
    }
});

// Handle Form Submit
authForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    authSubmitBtn.disabled = true;
    authSubmitBtn.textContent = "PLEASE WAIT...";
    authMessage.textContent = "";

    const endpoint = isRegisterMode ? "/api/v1/auth/register" : "/api/v1/auth/login";

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: "POST",
            headers: requestHeaders,
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Authentication failed.");
        }

        if (isRegisterMode) {
            authMessage.textContent = "Account created! Please sign in.";
            authMessage.className = "auth-message success";
            isRegisterMode = false;
            authFormTitle.textContent = "Sign In";
            authSubtitle.textContent = "Enter your account details below.";
            authSubmitBtn.textContent = "SIGN IN";
            switchPrompt.textContent = "Don't have an account?";
            switchModeBtn.textContent = "Create Account";
            document.getElementById("password").value = "";
        } else {
            localStorage.setItem("watch_user", JSON.stringify(data.user));
            window.location.href = "index.html";
        }
    } catch (error) {
        authMessage.textContent = error.message;
        authMessage.className = "auth-message error";
        authSubmitBtn.textContent = isRegisterMode ? "CREATE ACCOUNT" : "SIGN IN";
    } finally {
        authSubmitBtn.disabled = false;
    }
});