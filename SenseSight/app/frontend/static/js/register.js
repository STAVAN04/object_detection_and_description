document.getElementById("password").addEventListener("input", function () {
        const password = this.value;
        const lengthCriteria = document.getElementById("length");
        const letterCriteria = document.getElementById("letter");
        const specialCriteria = document.getElementById("special");

        if (password.length >= 6) {
            lengthCriteria.querySelector(".dot").textContent = "🟢";
            lengthCriteria.style.color = "green";
        } else {
            lengthCriteria.querySelector(".dot").textContent = "🔴";
            lengthCriteria.style.color = "red";
        }

        const hasUpperCase = /[A-Z]/.test(password);
        const hasDigit = /\d/.test(password);
        if (hasUpperCase && hasDigit) {
            letterCriteria.querySelector(".dot").textContent = "🟢";
            letterCriteria.style.color = "green";
        } else {
            letterCriteria.querySelector(".dot").textContent = "🔴";
            letterCriteria.style.color = "red";
        }

        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        if (hasSpecialChar) {
            specialCriteria.querySelector(".dot").textContent = "🟢";
            specialCriteria.style.color = "green";
        } else {
            specialCriteria.querySelector(".dot").textContent = "🔴";
            specialCriteria.style.color = "red";
        }
    });

document.getElementById('submit').addEventListener('click', function (e) {
        e.preventDefault();

        const name = document.getElementById('full-name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        const ajax = new XMLHttpRequest();

        ajax.open('POST', "/auth/register", true);
        ajax.setRequestHeader('Content-Type', 'application/json');

        ajax.onload = function () {
            if (ajax.status === 201) {
                window.location.href = '/login';
            } else if (ajax.status === 400) {
                alert("Please provide details")
            } else {
                alert("User already exists");
            }
        };

        const userData = {
            name: name,
            email: email,
            password: password,
        };

        ajax.send(JSON.stringify(userData));

    });