document.addEventListener("DOMContentLoaded", () => {
    setupEventListeners();
});

function setupEventListeners() {
    document.querySelector(".logout-btn")?.addEventListener("click", showLogoutConfirmation);
    document.getElementById("passwordForm")?.addEventListener("submit", validatePasswordForm);
}

function toggleMenu() {
    const sideMenu = document.getElementById("sideMenu");
    const toggleBtn = document.querySelector(".toggle-btn");
    const mainContainer = document.querySelector(".main-container");

    sideMenu.classList.toggle("active");
    mainContainer.classList.toggle("shifted");
    // toggleBtn.classList.toggle("active");

    toggleBtn.querySelector(".toggle-icon").style.display = sideMenu.classList.contains("active") ? "none" : "block";
    toggleBtn.querySelector(".close-icon").style.display = sideMenu.classList.contains("active") ? "block" : "none";
}

function blurBackground(state) {
    const mainContainer = document.querySelector(".main-container");
    if (state) {
        mainContainer.classList.add("blurred");
    } else {
        mainContainer.classList.remove("blurred");
    }
}

function openProfileDetails() {
    document.getElementById("profileDetails").classList.add("active");
    blurBackground(true);
}

function closeProfileDetails() {
    document.getElementById("profileDetails").classList.remove("active");
    blurBackground(false);
}

function showLogoutConfirmation() {
    document.getElementById("logoutPopup").classList.add("active");
    blurBackground(true);
}

function closeLogoutPopup() {
    document.getElementById("logoutPopup").classList.remove("active");
    blurBackground(false);
}

function logout() {
    closeLogoutPopup();
    const ajax = new XMLHttpRequest();
    ajax.open("POST", "/auth/logout", true);
    ajax.withCredentials = true;

    ajax.onload = function () {
        if (ajax.status === 200) {
            window.location.href = "/login";
        } else {
            alert("Error in logging out");
        }
    };

    ajax.onerror = function () {
        alert("Error in logging out");
    };

    ajax.send();
}

let detectionInterval;
let previousObjectCount = null;

async function fetchAndStoreDetection() {
    try{
        const getCountResponse = await fetch("http://127.0.0.1:8080/get_object_count",{
            method: "GET",
            credentials: "include"
        });

        if (!getCountResponse.ok) {
            console.warn("Object count data not available yet, skipping this cycle.");
            return;
        }

        const objectCountData = await getCountResponse.json();
        if (!objectCountData.object_count || Object.keys(objectCountData.object_count).length === 0 ||
            JSON.stringify(previousObjectCount) === JSON.stringify(objectCountData.object_count)) {
            return;
        }
        previousObjectCount = objectCountData.object_count;
        // console.log(objectCountData)
        const storeResponse = await fetch("http://127.0.0.1:8000/dashboard/store_detection",{
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ object_count: objectCountData.object_count }),
            credentials: "include"
        });
        // Handle store response
        if (!storeResponse.ok) {
            const error = await storeResponse.json();
            console.error("Store error:", error.detail);
            return;
        }

    } catch (error) {
        console.error("Error:", error);
    }
}

function startDetectionPolling() {
    detectionInterval = setInterval(fetchAndStoreDetection, 3000);
}

function stopDetectionPolling() {
    clearInterval(detectionInterval);
}

function showDetectionPopup() {
    document.getElementById("detectionPopup").style.display = "flex";
    document.getElementById("apiFrame").src = "http://127.0.0.1:8080/";
    startDetectionPolling()
}

function closeDetectionPopup() {
    document.getElementById("detectionPopup").style.display = "none";
    document.getElementById("apiFrame").src = ""; // Stop API call
    stopDetectionPolling()
}