document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('buyerSearchForm');
    const btnSubmit = document.getElementById('btnSubmitSearch');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const category = document.getElementById('id_category').value;
            const state = document.getElementById('id_state').value;
            const city = document.getElementById('id_city').value;
            const radius_km = document.getElementById('id_radius').value;

            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '⏳ Running Discovery Pipeline (Geocoding & Scraping)...';

            try {
                const data = await window.apiFetch('/api/buyers/search/', {
                    method: 'POST',
                    body: JSON.stringify({ category, state, city, radius_km })
                });

                if (data.id) {
                    window.location.href = `/results/${data.id}/`;
                } else {
                    alert('Search failed. Please try again.');
                    btnSubmit.disabled = false;
                    btnSubmit.innerHTML = '✨ Start Discovery Pipeline & Find Buyers →';
                }
            } catch (err) {
                alert(`Search Error: ${err.message}`);
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = '✨ Start Discovery Pipeline & Find Buyers →';
            }
        });
    }
});
