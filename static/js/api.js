/**
 * Shared API Helper module for fetch calls with CSRF header & JSON handling.
 */
async function apiFetch(url, options = {}) {
    let csrfToken = window.CSRF_TOKEN || '';
    if (!csrfToken) {
        const match = document.cookie.match(/csrftoken=([\w-]+)/);
        if (match) csrfToken = match[1];
    }

    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        ...(options.headers || {})
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const errorMsg = data.error?.message || data.detail || `Server error (${response.status})`;
        throw new Error(errorMsg);
    }

    return data;
}

window.apiFetch = apiFetch;
