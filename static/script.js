async function loginUser(event) {
    event.preventDefault();
    
    const formData = new FormData(document.getElementById('login-form'));

    try {
        const response = await fetch('/login', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();

            localStorage.setItem('user_display_name', data.username);

            window.location.href = data.redirect_url;
        } else {
            alert("Ошибка! Логин и пароль");
        }
    } catch (error) {
        console.error("Ошибка сети", error)
    }
}