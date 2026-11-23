const API_URL = "https://watch-api-eight.vercel.app";
const API_KEY = "watch-api-001";

const authForm = document.getElementById("authForm");
const authFormTitle = document.getElementById("authFormTitle");
const authSubtitle = document.getElementById("authSubtitle");
const authSubmitBtn = document.getElementById("authSubmitBtn");
const authMessage = document.getElementById("authMessage");
const switchPrompt = document.getElementById("switchPrompt");
const switchModeBtn = document.getElementById("switchModeBtn");
const guestLoginBtn = document.getElementById("guestLoginBtn");

let isRegisterMode = false;

// Toggle between Sign In and Create Account
switchModeBtn.addEventListener("click", () => {
    isRegisterMode = !isRegisterMode;
    authMessage.textContent = "";
    authMessage.className = "auth-message";

    if (isRegisterMode) {
        authFormTitle.textContent = "Create Account";
        authSubtitle.textContent = "3-20 letters/numbers/underscores. Password: 8+ chars with a letter & number.";
        authSubmitBtn.textContent = "CREATE ACCOUNT";
        switchPrompt.textContent = "Already have an account?";
        switchModeBtn.textContent = "Sign In";
    } else {
        authFormTitle.textContent = "Welcome back";
        authSubtitle.textContent = "Sign in to browse the full collection.";
        authSubmitBtn.textContent = "SIGN IN";
        switchPrompt.textContent = "Don't have an account?";
        switchModeBtn.textContent = "Create Account";
    }
});

// Handle Sign In or Registration
authForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (isRegisterMode) {
        if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
            authMessage.textContent = "Username must be 3-20 characters using letters, numbers, or underscores only.";
            authMessage.className = "auth-message error";
            return;
        }
        if (password.length < 8 || !/[A-Za-z]/.test(password) || !/\d/.test(password)) {
            authMessage.textContent = "Password must be at least 8 characters and include a letter and a number.";
            authMessage.className = "auth-message error";
            return;
        }
    }

    authSubmitBtn.disabled = true;
    authMessage.textContent = isRegisterMode ? "Creating account..." : "Signing in...";
    authMessage.className = "auth-message";

    const endpoint = isRegisterMode ? `${API_URL}/api/v1/auth/register` : `${API_URL}/api/v1/auth/login`;

    try {
        const res = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": API_KEY
            },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (!res.ok) {
            const detailMsg = Array.isArray(data.detail)
                ? data.detail[0]?.msg || "Invalid input."
                : (data.detail || "Authentication failed.");
            throw new Error(detailMsg);
        }

        if (isRegisterMode) {
            // Automatically log in after successful registration
            const loginRes = await fetch(`${API_URL}/api/v1/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY
                },
                body: JSON.stringify({ username, password })
            });
            const loginData = await loginRes.json();
            if (loginRes.ok) {
                localStorage.setItem("watch_user", JSON.stringify(loginData.user));
                window.location.href = "index.html";
                return;
            }
        }

        localStorage.setItem("watch_user", JSON.stringify(data.user));
        window.location.href = "index.html";
    } catch (err) {
        authMessage.textContent = err.message || "Unable to connect to server.";
        authMessage.className = "auth-message error";
    } finally {
        authSubmitBtn.disabled = false;
    }
});

// Guest Preview Access (Limited to 10 watches, no favorites/reviews)
guestLoginBtn.addEventListener("click", () => {
    localStorage.setItem("watch_user", JSON.stringify({ username: "Guest", role: "guest" }));
    window.location.href = "index.html";
});