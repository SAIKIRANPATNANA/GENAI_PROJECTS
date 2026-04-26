document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const showRegister = document.getElementById('showRegister');
    const showLogin = document.getElementById('showLogin');

    showRegister.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.auth-box').forEach(box => {
            box.style.display = box.style.display === 'none' ? 'block' : 'none';
        });
    });

    showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.auth-box').forEach(box => {
            box.style.display = box.style.display === 'none' ? 'block' : 'none';
        });
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            email: document.getElementById('email').value,
            password: document.getElementById('password').value
        };

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (response.ok) {
                window.location.href = '/';
            } else {
                alert(data.error);
            }
        } catch (error) {
            alert('An error occurred during login');
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('regName').value,
            email: document.getElementById('regEmail').value,
            password: document.getElementById('regPassword').value,
            role: document.getElementById('regRole').value
        };

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (response.ok) {
                alert('Registration successful! Please login.');
                showLogin.click();
            } else {
                alert(data.error);
            }
        } catch (error) {
            alert('An error occurred during registration');
        }
    });
}); 