// Route Guard, Role Check & Logout
const rawUser = localStorage.getItem("watch_user");
if (!rawUser) {
    window.location.href = "login.html";
}

const currentUser = rawUser ? JSON.parse(rawUser) : { username: "Guest", role: "guest" };
const userRole = currentUser.role || "guest";
const isGuest = userRole === "guest";
const isAdmin = userRole === "admin";

const roleBadge = document.getElementById("userRoleBadge");
if (roleBadge) {
    roleBadge.textContent = userRole.toUpperCase();
}

if (isAdmin) {
    const auditBtn = document.getElementById("auditLogNavBtn");
    if (auditBtn) auditBtn.style.display = "inline-block";

    const addWatchBtn = document.getElementById("addWatchBtn");
    if (addWatchBtn) addWatchBtn.style.display = "inline-block";
}

if (!isGuest) {
    const favFilterBtn = document.getElementById("favoritesFilterBtn");
    if (favFilterBtn) favFilterBtn.style.display = "inline-block";
}

function logoutUser() {
    localStorage.removeItem("watch_user");
    window.location.href = "login.html";
}

const API_URL = "https://watch-api-eight.vercel.app";

// Include API Key header if using the protected /api/v1/ routes
const API_KEY = "watch-api-001";
const requestHeaders = {
    "x-api-key": API_KEY
};

const jsonHeaders = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
};

function getAdminHeaders(includeJson = false) {
    const headers = {
        "x-api-key": API_KEY
    };
    if (currentUser && currentUser.id) {
        headers["x-user-id"] = String(currentUser.id);
    }
    if (includeJson) {
        headers["Content-Type"] = "application/json";
    }
    return headers;
}

let allWatches = [];
let featuredWatches = [];
let favoriteWatchIds = new Set();
let showingFavoritesOnly = false;
let activeModalWatch = null;
let editingWatchId = null;
let pendingDeleteConfirm = false;
let currentHeroIndex = 0;
let selectedBrand = "";
let isHeroAnimating = false;

// FETCH WATCHES & USER FAVORITES
async function loadWatches() {
    try {
        let response = await fetch(`${API_URL}/watches`);
        if (!response.ok) {
            response = await fetch(`${API_URL}/api/v1/watches`, { headers: requestHeaders });
        }

        const data = await response.json();
        allWatches = isGuest ? data.watches.slice(0, 10) : data.watches;
        featuredWatches = allWatches.slice(0, 5);

        if (!isGuest && currentUser.id) {
            await loadUserFavorites();
        }

        refreshCurrentView();
        if (featuredWatches.length > 0) {
            updateHero(0);
        }

        if (isGuest && !document.querySelector(".guest-limit-banner")) {
            const catalogContainer = document.querySelector(".catalog-container");
            const notice = document.createElement("p");
            notice.className = "guest-limit-banner";
            notice.innerHTML = `Guest Preview: Showing first 10 watches only. <button type="button" onclick="logoutUser()">Sign in with an account</button> to unlock all timepieces.`;
            catalogContainer.appendChild(notice);
        }
    } catch (error) {
        console.error(error);
        document.getElementById("watchGrid").innerHTML = "<p style='grid-column: 1/-1; text-align:center; color:#3D3D3D;'>Unable to connect to the Horology API.</p>";
    }
}

function refreshCurrentView() {
    if (showingFavoritesOnly) {
        displayWatches(allWatches.filter(w => favoriteWatchIds.has(w.id)));
    } else if (selectedBrand) {
        displayWatches(allWatches.filter(w => w.brand.toLowerCase() === selectedBrand.toLowerCase()));
    } else {
        displayWatches(allWatches);
    }
}

async function loadUserFavorites() {
    try {
        const res = await fetch(`${API_URL}/api/v1/users/${currentUser.id}/favorites`, { headers: requestHeaders });
        if (res.ok) {
            const data = await res.json();
            favoriteWatchIds = new Set(data.favorites.map(w => w.id));
        }
    } catch (err) {
        console.error(err);
    }
}

// RENDER GRID
function displayWatches(watches) {
    const grid = document.getElementById("watchGrid");
    grid.innerHTML = "";

    if (!watches || watches.length === 0) {
        grid.innerHTML = "<p style='grid-column: 1/-1; text-align:center; color:#3D3D3D; padding: 40px 0;'>No timepieces found matching your selection.</p>";
        return;
    }

    watches.forEach(watch => {
        const card = document.createElement("div");
        card.className = "watch-card";
        card.onclick = () => openModal(watch);

        const isFav = favoriteWatchIds.has(watch.id);
        const favTag = isFav ? `<span class="card-fav-dot" title="Saved in Favorites">&#9733;</span>` : "";

        card.innerHTML = `
            <div class="card-top">
                ${favTag}
                <img src="${watch.image}" alt="${watch.model}" onerror="this.src='https://placehold.co/300x300/336659/FDFDFD?text=${encodeURIComponent(watch.brand)}'">
            </div>
            <div class="card-bottom">
                <p class="card-brand">${watch.brand}</p>
                <h4 class="card-title">${watch.model} "${watch.nickname}"</h4>
            </div>
        `;

        grid.appendChild(card);
    });
}

// FAVORITES FILTER & TOGGLE
function toggleFavoritesFilter() {
    const btn = document.getElementById("favoritesFilterBtn");
    showingFavoritesOnly = !showingFavoritesOnly;

    document.querySelectorAll(".brand-circle").forEach(b => b.classList.remove("active"));
    document.getElementById("searchInput").value = "";
    selectedBrand = "";

    if (showingFavoritesOnly) {
        btn.classList.add("active");
        const favWatches = allWatches.filter(w => favoriteWatchIds.has(w.id));
        displayWatches(favWatches);
    } else {
        btn.classList.remove("active");
        displayWatches(allWatches);
    }
}

function updateModalFavoriteButton() {
    const favBtn = document.getElementById("modalFavBtn");
    if (!favBtn || !activeModalWatch) return;

    if (isGuest) {
        favBtn.innerHTML = "&#9734;";
        favBtn.title = "Sign in to save to favorites";
        favBtn.classList.remove("saved");
        return;
    }

    const isFav = favoriteWatchIds.has(activeModalWatch.id);
    favBtn.innerHTML = isFav ? "&#9733;" : "&#9734;";
    favBtn.title = isFav ? "Saved in Favorites" : "Save to Favorites";
    favBtn.classList.toggle("saved", isFav);
}

async function toggleWatchFavorite() {
    if (!activeModalWatch) return;
    if (isGuest || !currentUser.id) {
        logoutUser();
        return;
    }

    const watchId = activeModalWatch.id;
    const isFav = favoriteWatchIds.has(watchId);

    try {
        if (isFav) {
            const res = await fetch(`${API_URL}/api/v1/favorites/${currentUser.id}/${watchId}`, {
                method: "DELETE",
                headers: requestHeaders
            });
            if (res.ok) favoriteWatchIds.delete(watchId);
        } else {
            const res = await fetch(`${API_URL}/api/v1/favorites`, {
                method: "POST",
                headers: jsonHeaders,
                body: JSON.stringify({ user_id: currentUser.id, watch_id: watchId })
            });
            if (res.ok) favoriteWatchIds.add(watchId);
        }

        updateModalFavoriteButton();
        refreshCurrentView();
    } catch (err) {
        console.error(err);
    }
}

// REVIEWS (1-5 STARS + SHORT COMMENT + DELETE OWN/ADMIN)
async function loadWatchReviews(watchId) {
    const listEl = document.getElementById("modalReviewsList");
    const summaryEl = document.getElementById("modalRatingSummary");
    listEl.innerHTML = "<p class='review-empty'>Loading reviews...</p>";

    try {
        const res = await fetch(`${API_URL}/api/v1/watches/${watchId}/reviews`, { headers: requestHeaders });
        if (!res.ok) throw new Error("Failed to load reviews.");

        const data = await res.json();
        if (data.count === 0) {
            summaryEl.textContent = "No ratings yet";
            listEl.innerHTML = "<p class='review-empty'>No reviews yet.</p>";
            return;
        }

        summaryEl.textContent = `${data.average_rating} / 5 (${data.count})`;
        listEl.innerHTML = "";

        data.reviews.forEach(rev => {
            const stars = "★".repeat(rev.rating) + "☆".repeat(5 - rev.rating);
            const canDelete = isAdmin || (!isGuest && currentUser.id === rev.user_id);
            const deleteBtnHtml = canDelete
                ? `<button type="button" class="review-delete-btn" onclick="deleteWatchReview(${rev.id})" title="Delete Review">&times;</button>`
                : "";

            const item = document.createElement("div");
            item.className = "review-item";
            item.innerHTML = `
                <div class="review-item-top">
                    <span class="review-author">${rev.username}</span>
                    <div class="review-item-right">
                        <span class="review-stars">${stars}</span>
                        ${deleteBtnHtml}
                    </div>
                </div>
                <p class="review-text">${rev.comment}</p>
            `;
            listEl.appendChild(item);
        });
    } catch (err) {
        summaryEl.textContent = "";
        listEl.innerHTML = "<p class='review-empty'>Unable to load reviews.</p>";
    }
}

async function deleteWatchReview(reviewId) {
    if (isGuest || !currentUser.id || !activeModalWatch) return;

    try {
        const res = await fetch(`${API_URL}/api/v1/reviews/${reviewId}`, {
            method: "DELETE",
            headers: getAdminHeaders(false)
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Failed to delete review.");
        }

        await loadWatchReviews(activeModalWatch.id);
    } catch (err) {
        alert(err.message || "Unable to delete review.");
    }
}

async function submitWatchReview(event) {
    event.preventDefault();
    if (!activeModalWatch || isGuest || !currentUser.id) return;

    const rating = parseInt(document.getElementById("reviewRating").value, 10);
    const commentInput = document.getElementById("reviewComment");
    const comment = commentInput.value.trim();
    if (!comment) return;

    try {
        const res = await fetch(`${API_URL}/api/v1/watches/${activeModalWatch.id}/reviews`, {
            method: "POST",
            headers: jsonHeaders,
            body: JSON.stringify({
                user_id: currentUser.id,
                rating: rating,
                comment: comment
            })
        });

        if (res.ok) {
            commentInput.value = "";
            await loadWatchReviews(activeModalWatch.id);
        }
    } catch (err) {
        console.error(err);
    }
}

// ADMIN CRUD: ADD, EDIT & DELETE WATCHES
function openWatchFormModal(watchToEdit = null) {
    if (!isAdmin) return;

    const form = document.getElementById("watchCrudForm");
    const titleEl = document.getElementById("watchFormModalTitle");
    const submitBtn = document.getElementById("watchFormSubmitBtn");
    const msgEl = document.getElementById("watchFormMessage");

    form.reset();
    msgEl.textContent = "";
    msgEl.className = "form-feedback-msg";

    if (watchToEdit) {
        editingWatchId = watchToEdit.id;
        titleEl.textContent = `Edit ${watchToEdit.brand} ${watchToEdit.model}`;
        submitBtn.textContent = "UPDATE WATCH";

        document.getElementById("wfBrand").value = watchToEdit.brand || "Rolex";
        document.getElementById("wfModel").value = watchToEdit.model || "";
        document.getElementById("wfNickname").value = watchToEdit.nickname || "";
        document.getElementById("wfReference").value = watchToEdit.reference_number || "";
        document.getElementById("wfCaseMaterial").value = watchToEdit.case_material || "";
        document.getElementById("wfCaseSize").value = watchToEdit.case_size_mm || "";
        document.getElementById("wfDialColor").value = watchToEdit.dial_color || "";
        document.getElementById("wfBezelMaterial").value = watchToEdit.bezel_material || "";
        document.getElementById("wfMovementType").value = watchToEdit.movement_type || "Automatic";
        document.getElementById("wfMovement").value = watchToEdit.movement || "";
        document.getElementById("wfPowerReserve").value = watchToEdit.power_reserve_hours || "";
        document.getElementById("wfWaterResistance").value = watchToEdit.water_resistance_m || "";
        document.getElementById("wfYear").value = watchToEdit.year || 2024;
        document.getElementById("wfCategory").value = watchToEdit.category || "Sports";
        document.getElementById("wfOrigin").value = watchToEdit.origin || "Switzerland";
        document.getElementById("wfPrice").value = watchToEdit.price_php || "";
        document.getElementById("wfImage").value = watchToEdit.image || "";
        document.getElementById("wfDescription").value = watchToEdit.description || "";
    } else {
        editingWatchId = null;
        titleEl.textContent = "Add New Timepiece";
        submitBtn.textContent = "CREATE WATCH";
    }

    document.getElementById("watchFormModal").classList.add("open");
}

function openEditWatchModal() {
    if (!isAdmin || !activeModalWatch) return;
    const watchCopy = { ...activeModalWatch };
    closeModal();
    openWatchFormModal(watchCopy);
}

function closeWatchFormModal() {
    document.getElementById("watchFormModal").classList.remove("open");
    editingWatchId = null;
}

async function submitWatchForm(event) {
    event.preventDefault();
    if (!isAdmin) return;

    const submitBtn = document.getElementById("watchFormSubmitBtn");
    const msgEl = document.getElementById("watchFormMessage");

    const payload = {
        brand: document.getElementById("wfBrand").value,
        model: document.getElementById("wfModel").value.trim(),
        nickname: document.getElementById("wfNickname").value.trim(),
        reference_number: document.getElementById("wfReference").value.trim(),
        case_material: document.getElementById("wfCaseMaterial").value.trim(),
        case_size_mm: parseFloat(document.getElementById("wfCaseSize").value),
        dial_color: document.getElementById("wfDialColor").value.trim(),
        bezel_material: document.getElementById("wfBezelMaterial").value.trim(),
        movement_type: document.getElementById("wfMovementType").value,
        movement: document.getElementById("wfMovement").value.trim(),
        power_reserve_hours: parseInt(document.getElementById("wfPowerReserve").value, 10),
        water_resistance_m: parseInt(document.getElementById("wfWaterResistance").value, 10),
        year: parseInt(document.getElementById("wfYear").value, 10),
        origin: document.getElementById("wfOrigin").value,
        category: document.getElementById("wfCategory").value,
        price_php: parseInt(document.getElementById("wfPrice").value, 10),
        image: document.getElementById("wfImage").value.trim(),
        description: document.getElementById("wfDescription").value.trim()
    };

    const isEditing = editingWatchId !== null;
    const endpoint = isEditing
        ? `${API_URL}/api/v1/watches/${editingWatchId}`
        : `${API_URL}/api/v1/watches`;
    const method = isEditing ? "PATCH" : "POST";

    submitBtn.disabled = true;
    msgEl.textContent = isEditing ? "Updating timepiece..." : "Saving timepiece...";
    msgEl.className = "form-feedback-msg";

    try {
        const res = await fetch(endpoint, {
            method: method,
            headers: getAdminHeaders(true),
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || "Failed to save watch.");
        }

        await loadWatches();
        closeWatchFormModal();
    } catch (err) {
        msgEl.textContent = err.message || "Error saving watch.";
        msgEl.className = "form-feedback-msg error";
    } finally {
        submitBtn.disabled = false;
    }
}

async function handleDeleteWatch() {
    if (!isAdmin || !activeModalWatch) return;

    const delBtn = document.getElementById("adminDeleteBtn");
    if (!pendingDeleteConfirm) {
        pendingDeleteConfirm = true;
        delBtn.textContent = "CONFIRM DELETE?";
        delBtn.classList.add("confirming");
        return;
    }

    const watchId = activeModalWatch.id;
    delBtn.disabled = true;
    delBtn.textContent = "DELETING...";

    try {
        const res = await fetch(`${API_URL}/api/v1/watches/${watchId}`, {
            method: "DELETE",
            headers: getAdminHeaders(false)
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Failed to delete watch.");
        }

        favoriteWatchIds.delete(watchId);
        closeModal();
        await loadWatches();
    } catch (err) {
        alert(err.message || "Unable to delete timepiece.");
        delBtn.disabled = false;
        delBtn.textContent = "DELETE";
        delBtn.classList.remove("confirming");
        pendingDeleteConfirm = false;
    }
}

// ADMIN AUDIT LOGS MODAL
async function openAuditModal() {
    if (!isAdmin) return;
    const modal = document.getElementById("auditModal");
    const listEl = document.getElementById("auditLogsList");
    listEl.innerHTML = "<p class='review-empty'>Loading activity logs...</p>";
    modal.classList.add("open");

    try {
        const res = await fetch(`${API_URL}/api/v1/audit-logs?limit=30`, {
            headers: getAdminHeaders(false)
        });
        const data = await res.json();

        if (!res.ok) {
            listEl.innerHTML = `<p class='review-empty'>${data.detail || "Unable to load activity logs."}</p>`;
            return;
        }

        if (!data.logs || data.logs.length === 0) {
            listEl.innerHTML = "<p class='review-empty'>No activity recorded yet.</p>";
            return;
        }

        listEl.innerHTML = "";
        data.logs.forEach(log => {
            const timeStr = new Date(log.created_at).toLocaleString();
            const actor = log.username || "System";
            const row = document.createElement("div");
            row.className = "audit-log-item";
            row.innerHTML = `
                <div class="audit-log-top">
                    <span class="audit-action">${log.action}</span>
                    <span class="audit-time">${timeStr}</span>
                </div>
                <p class="audit-details"><strong>${actor}:</strong> ${log.details || ""}</p>
            `;
            listEl.appendChild(row);
        });
    } catch (err) {
        listEl.innerHTML = "<p class='review-empty'>Unable to load activity logs.</p>";
    }
}

function closeAuditModal() {
    document.getElementById("auditModal").classList.remove("open");
}

// HERO UPDATE
function updateHero(index) {
    if (!featuredWatches || featuredWatches.length === 0) return;
    currentHeroIndex = index;
    const watch = featuredWatches[currentHeroIndex];

    document.getElementById("heroBrand").innerText = watch.brand.toUpperCase();
    document.getElementById("heroTitle").innerText = `${watch.model} "${watch.nickname}"`;
    document.getElementById("heroDesc").innerText = watch.description;
    document.getElementById("heroRef").innerText = `Ref. ${watch.reference_number}`;
    document.getElementById("heroMaterial").innerText = watch.case_material;

    const heroImg = document.getElementById("heroImage");
    heroImg.src = watch.image;
    heroImg.onerror = () => {
        heroImg.src = `https://placehold.co/500x500/1F493D/F3EFE8?text=${encodeURIComponent(watch.model)}`;
    };

    const heroPagination = document.getElementById("heroPagination");
    if (heroPagination) {
        const currentNum = String(currentHeroIndex + 1).padStart(2, '0');
        const totalNum = String(featuredWatches.length).padStart(2, '0');
        heroPagination.innerText = `N° ${currentNum} / ${totalNum}`;
    }
}

// DEPTH ZOOM TRANSITION
function transitionHero(nextIndex, direction = "next") {
    if (isHeroAnimating || !featuredWatches || featuredWatches.length === 0) return;
    isHeroAnimating = true;

    const heroImg = document.getElementById("heroImage");
    const heroContent = document.querySelector(".hero-content");

    const exitClass = direction === "next" ? "zoom-exit-left" : "zoom-exit-right";
    heroImg.classList.add(exitClass);
    heroContent.classList.add("text-exit");

    setTimeout(() => {
        updateHero(nextIndex);

        heroImg.classList.remove(exitClass);
        heroContent.classList.remove("text-exit");

        const enterClass = direction === "next" ? "zoom-enter-right" : "zoom-enter-left";
        heroImg.classList.add(enterClass);
        heroContent.classList.add("text-enter");

        void heroImg.offsetWidth;
        void heroContent.offsetWidth;

        heroImg.classList.remove(enterClass);
        heroContent.classList.remove("text-enter");

        setTimeout(() => {
            isHeroAnimating = false;
        }, 500);
    }, 280);
}

// HERO NAVIGATION
function prevHeroWatch() {
    if (featuredWatches.length === 0) return;
    const prevIndex = (currentHeroIndex - 1 + featuredWatches.length) % featuredWatches.length;
    transitionHero(prevIndex, "prev");
}

function nextHeroWatch() {
    if (featuredWatches.length === 0) return;
    const nextIndex = (currentHeroIndex + 1) % featuredWatches.length;
    transitionHero(nextIndex, "next");
}

// SEARCH
async function searchWatches() {
    const query = document.getElementById("searchInput").value.trim();
    
    document.querySelectorAll(".brand-circle").forEach(btn => btn.classList.remove("active"));
    const favBtn = document.getElementById("favoritesFilterBtn");
    if (favBtn) favBtn.classList.remove("active");
    showingFavoritesOnly = false;
    selectedBrand = "";

    if (!query) {
        displayWatches(allWatches);
        return;
    }

    if (isGuest) {
        const filtered = allWatches.filter(w => 
            w.brand.toLowerCase().includes(query.toLowerCase()) ||
            w.model.toLowerCase().includes(query.toLowerCase()) ||
            w.nickname.toLowerCase().includes(query.toLowerCase()) ||
            w.reference_number.toLowerCase().includes(query.toLowerCase()) ||
            (w.category && w.category.toLowerCase().includes(query.toLowerCase()))
        );
        displayWatches(filtered);
        return;
    }

    try {
        let response = await fetch(`${API_URL}/watches/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            response = await fetch(`${API_URL}/api/v1/watches/search?q=${encodeURIComponent(query)}`, { headers: requestHeaders });
        }
        const data = await response.json();
        displayWatches(data.results);
    } catch (error) {
        const filtered = allWatches.filter(w => 
            w.brand.toLowerCase().includes(query.toLowerCase()) ||
            w.model.toLowerCase().includes(query.toLowerCase()) ||
            w.nickname.toLowerCase().includes(query.toLowerCase()) ||
            w.reference_number.toLowerCase().includes(query.toLowerCase()) ||
            (w.category && w.category.toLowerCase().includes(query.toLowerCase()))
        );
        displayWatches(filtered);
    }
}

// BRAND FILTER
function toggleBrandFilter(brandName, element) {
    const isAlreadySelected = element.classList.contains("active");

    document.querySelectorAll(".brand-circle").forEach(btn => btn.classList.remove("active"));
    const favBtn = document.getElementById("favoritesFilterBtn");
    if (favBtn) favBtn.classList.remove("active");
    showingFavoritesOnly = false;
    document.getElementById("searchInput").value = "";

    if (isAlreadySelected) {
        selectedBrand = "";
        displayWatches(allWatches);
    } else {
        selectedBrand = brandName;
        element.classList.add("active");
        const filtered = allWatches.filter(w => w.brand.toLowerCase() === brandName.toLowerCase());
        displayWatches(filtered);
    }
}

// MODAL (Populates full technical details, favorite state & reviews)
function openModal(watch) {
    activeModalWatch = watch;
    pendingDeleteConfirm = false;

    const adminActions = document.getElementById("modalAdminActions");
    const delBtn = document.getElementById("adminDeleteBtn");
    if (adminActions) {
        adminActions.style.display = isAdmin ? "flex" : "none";
    }
    if (delBtn) {
        delBtn.disabled = false;
        delBtn.textContent = "DELETE";
        delBtn.classList.remove("confirming");
    }

    document.getElementById("modalBrand").innerText = watch.brand;
    document.getElementById("modalTitle").innerText = watch.model;
    document.getElementById("modalNickname").innerText = `"${watch.nickname}"`;
    document.getElementById("modalRef").innerText = watch.reference_number;
    document.getElementById("modalMaterial").innerText = watch.case_material;
    document.getElementById("modalDescription").innerText = watch.description;

    const sizeVal = watch.case_size_mm ? `${watch.case_size_mm} mm` : (watch.case_size || "N/A");
    document.getElementById("modalSize").innerText = sizeVal;
    document.getElementById("modalDial").innerText = watch.dial_color || "N/A";
    document.getElementById("modalMovement").innerText = watch.movement || "N/A";

    const powerVal = watch.power_reserve_hours ? `${watch.power_reserve_hours} Hours` : (watch.power_reserve || "N/A");
    document.getElementById("modalPower").innerText = powerVal;

    const wrVal = watch.water_resistance_m ? `${watch.water_resistance_m} m` : (watch.water_resistance || "N/A");
    document.getElementById("modalWR").innerText = wrVal;

    const catYear = `${watch.category || "Luxury"} (${watch.year || "Classic"})`;
    document.getElementById("modalCatYear").innerText = catYear;

    const priceFormatted = watch.price_php ? `₱${watch.price_php.toLocaleString()}` : "Price upon request";
    document.getElementById("modalPrice").innerText = priceFormatted;

    const modalImg = document.getElementById("modalImage");
    modalImg.src = watch.image;
    modalImg.onerror = () => {
        modalImg.src = `https://placehold.co/400x400/336659/FDFDFD?text=${encodeURIComponent(watch.model)}`;
    };

    const reviewForm = document.getElementById("reviewForm");
    const reviewHint = document.getElementById("reviewGuestHint");
    if (isGuest) {
        reviewForm.style.display = "none";
        reviewHint.style.display = "block";
    } else {
        reviewForm.style.display = "flex";
        reviewHint.style.display = "none";
    }

    updateModalFavoriteButton();
    loadWatchReviews(watch.id);

    document.getElementById("detailModal").classList.add("open");
}

function closeModal() {
    document.getElementById("detailModal").classList.remove("open");
    activeModalWatch = null;
    pendingDeleteConfirm = false;
}

function handleBackdropClick(event) {
    if (event.target.id === "detailModal") {
        closeModal();
    }
    if (event.target.id === "watchFormModal") {
        closeWatchFormModal();
    }
    if (event.target.id === "auditModal") {
        closeAuditModal();
    }
}

// PARALLAX & SPOTLIGHT
const heroSection = document.getElementById("hero");
if (heroSection) {
    heroSection.addEventListener("mousemove", (e) => {
        if (isHeroAnimating) return;

        const rect = heroSection.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        heroSection.style.setProperty("--mouse-x", `${mouseX}px`);
        heroSection.style.setProperty("--mouse-y", `${mouseY}px`);

        const percentX = (mouseX / rect.width) - 0.5;
        const percentY = (mouseY / rect.height) - 0.5;

        const heroImg = document.getElementById("heroImage");
        if (heroImg) {
            const shiftX = percentX * -24;
            const shiftY = percentY * -24;
            heroImg.style.transform = `translate(${shiftX}px, ${shiftY}px)`;
        }
    });

    heroSection.addEventListener("mouseleave", () => {
        const heroImg = document.getElementById("heroImage");
        if (heroImg && !isHeroAnimating) {
            heroImg.style.transform = "translate(0px, 0px)";
        }
    });
}

// EVENTS
document.getElementById("searchInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") searchWatches();
});

loadWatches();