document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('buyerSearchForm');
    const btnSubmit = document.getElementById('btnSubmitSearch');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const category = document.getElementById('id_category').value;
            const state = document.getElementById('id_state').value;
            const city = document.getElementById('id_city').value.trim();
            const radius_km = document.getElementById('id_radius').value;

            if (!city) {
                alert('Please enter a US city name.');
                return;
            }

            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '⏳ Running Discovery Pipeline (Geocoding & Scraping)...';

            try {
                const data = await window.apiFetch('/api/buyers/search/', {
                    method: 'POST',
                    body: JSON.stringify({ category, state, city, radius_km })
                });

                if (data && data.id) {
                    if (data.status === 'failed') {
                        alert(`Discovery error: ${data.error_message || 'Could not find buyers in this location.'}`);
                        btnSubmit.disabled = false;
                        btnSubmit.innerHTML = '✨ Start Discovery Pipeline & Find Buyers →';
                    } else {
                        window.location.href = `/results/${data.id}/`;
                    }
                } else {
                    alert('Search failed. Please try again.');
                    btnSubmit.disabled = false;
                    btnSubmit.innerHTML = '✨ Start Discovery Pipeline & Find Buyers →';
                }
            } catch (err) {
                alert(`Search Error: ${err.message || 'An unexpected error occurred'}`);
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = '✨ Start Discovery Pipeline & Find Buyers →';
            }
        });
    }
});
