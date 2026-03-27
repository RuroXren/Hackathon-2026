async function handleAuth(event, url) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('user_display_name', data.username);
            window.location.href = data.redirect_url;
        } else {
            alert("Ошибка: " + (data.detail || "Неверные данные"));
        }
    } catch (error) {
        console.error("Ошибка сети:", error);
        alert("Сервер не отвечает");
    }
}