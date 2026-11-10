async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    sessionStorage.removeItem('token');

    try {
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        if (!response.ok) throw new Error('Credenciales inválidas o error del servidor');

        const data = await response.json();
        // SimpleJWT devuelve access, no data.token.
        sessionStorage.setItem('token', data.access);
        alert('Inicio de sesión exitoso');
    } catch (error) {
        console.error(error);
        alert('No fue posible iniciar sesión');
    }
}

async function loadUsers() {
    const token = sessionStorage.getItem('token');
    const list = document.getElementById('userList');
    list.textContent = '';

    try {
        const response = await fetch('/api/usuarios/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.status === 401) throw new Error('Inicia sesión o verifica tu token');
        if (response.status === 403) throw new Error('Se requiere rol ADMIN');
        if (!response.ok) throw new Error('No fue posible cargar los usuarios');

        const users = await response.json();
        users.forEach(user => {
            const item = document.createElement('li');
            item.textContent = user.nombre;
            list.appendChild(item);
        });
        if (users.length === 0) list.textContent = 'No hay usuarios del juego registrados.';
    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}
