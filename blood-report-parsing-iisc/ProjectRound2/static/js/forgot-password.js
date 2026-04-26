document.addEventListener('DOMContentLoaded', function() {
    // Forgot Password Modal
    const forgotPasswordLink = document.getElementById('forgotPasswordLink');
    const forgotPasswordModal = document.getElementById('forgotPasswordModal');
    const otpVerificationModal = document.getElementById('otpVerificationModal');
    let currentEmail = '';

    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', (e) => {
            e.preventDefault();
            forgotPasswordModal.style.display = 'block';
        });
    }

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === forgotPasswordModal) {
            forgotPasswordModal.style.display = 'none';
        }
        if (e.target === otpVerificationModal) {
            otpVerificationModal.style.display = 'none';
        }
    });

    // Handle forgot password form submission
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('forgotEmail').value;
            currentEmail = email;

            try {
                const response = await fetch('/forgot-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email })
                });

                const data = await response.json();
                if (response.ok) {
                    forgotPasswordModal.style.display = 'none';
                    otpVerificationModal.style.display = 'block';
                    alert('OTP sent to your email!');
                } else {
                    alert(data.error || 'Failed to send OTP');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    }

    // Handle OTP verification form submission
    const otpVerificationForm = document.getElementById('otpVerificationForm');
    if (otpVerificationForm) {
        otpVerificationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const otp = document.getElementById('otp').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (newPassword !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }

            try {
                const response = await fetch('/verify-otp', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email: currentEmail,
                        otp,
                        new_password: newPassword
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    alert('Password reset successful! Please login with your new password.');
                    otpVerificationModal.style.display = 'none';
                    window.location.href = '/login';
                } else {
                    alert(data.error || 'Failed to verify OTP');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    }
});
