 document.getElementById("submit").addEventListener("click", function (e) {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const ajax = new XMLHttpRequest();
        ajax.open("POST", "/auth/login", true);
        ajax.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        ajax.onload = function () {
            if (ajax.status === 200) {
                window.location.href = "/dashboard/home";
            } else if (ajax.status === 404) {
                alert("User not found");
            } else {
                alert("Invalid Credentials");
            }
        };
        ajax.send(formData.toString());
    });