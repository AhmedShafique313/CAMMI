// In production, use proper authentication and CSRF protection.
// The customer ID should come from your DB for the logged-in user.

document.addEventListener('DOMContentLoaded', () => {
  // Grab session_id from the query string after checkout
  const searchParams = new URLSearchParams(window.location.search);
  if (searchParams.has('session_id')) {
    const session_id = searchParams.get('session_id');
    const hiddenInput = document.getElementById('session-id');
    if (hiddenInput) {
      hiddenInput.value = session_id;
    }
  }

  // Handle "Manage Billing" button (success.html)
  const manageBtn = document.getElementById('manage-billing');
  if (manageBtn) {
    manageBtn.addEventListener('click', () => {
      const session_id = document.getElementById('session-id')?.value;
      if (!session_id) {
        alert("No session_id found.");
        return;
      }

      // Submit a hidden form to Flask, which redirects to Stripe portal
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = '/create-portal-session';

      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'session_id';
      input.value = session_id;

      form.appendChild(input);
      document.body.appendChild(form);
      form.submit();
    });
  }
});
