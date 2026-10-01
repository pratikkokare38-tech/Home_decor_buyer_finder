document.addEventListener('DOMContentLoaded', () => {
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const buyerCheckboxes = document.querySelectorAll('.buyer-checkbox');
    const btnCreateCampaign = document.getElementById('btnCreateCampaign');
    const selectedCountSpan = document.getElementById('selectedCount');
    const filterEmailStatus = document.getElementById('filterEmailStatus');
    const rows = document.querySelectorAll('.buyer-row');

    function updateSelectedState() {
        const checked = document.querySelectorAll('.buyer-checkbox:checked');
        const count = checked.length;

        if (selectedCountSpan) selectedCountSpan.textContent = count;
        if (btnCreateCampaign) btnCreateCampaign.disabled = count === 0;
    }

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', (e) => {
            const isChecked = e.target.checked;
            buyerCheckboxes.forEach(cb => {
                if (cb.closest('tr').style.display !== 'none') {
                    cb.checked = isChecked;
                }
            });
            updateSelectedState();
        });
    }

    buyerCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateSelectedState);
    });

    if (filterEmailStatus) {
        filterEmailStatus.addEventListener('change', (e) => {
            const val = e.target.value;
            rows.forEach(row => {
                const status = row.getAttribute('data-status');
                const hasEmail = row.getAttribute('data-has-email') === 'true';

                if (val === 'all') {
                    row.style.display = '';
                } else if (val === 'valid') {
                    row.style.display = status === 'valid' ? '' : 'none';
                } else if (val === 'has_email') {
                    row.style.display = hasEmail ? '' : 'none';
                }
            });
            updateSelectedState();
        });
    }

    if (btnCreateCampaign) {
        btnCreateCampaign.addEventListener('click', () => {
            const checkedIds = Array.from(document.querySelectorAll('.buyer-checkbox:checked'))
                                    .map(cb => cb.value);
            if (checkedIds.length > 0) {
                window.location.href = `/campaigns/compose/?buyers=${checkedIds.join(',')}`;
            }
        });
    }

    // Apply default filter on load
    if (filterEmailStatus) {
        filterEmailStatus.dispatchEvent(new Event('change'));
    }
});
