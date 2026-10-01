/**
 * Shared API Helper module for fetch calls with CSRF header & JSON handling.
 */
async function apiFetch(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': window.CSRF_TOKEN || '',
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
