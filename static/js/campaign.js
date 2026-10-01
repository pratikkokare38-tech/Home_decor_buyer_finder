function insertPlaceholder(token) {
    const bodyInput = document.getElementById('bodyInput');
    if (bodyInput) {
        const start = bodyInput.selectionStart;
        const end = bodyInput.selectionEnd;
        const text = bodyInput.value;
        bodyInput.value = text.substring(0, start) + token + text.substring(end);
        bodyInput.focus();
        updatePreview();
    }
}

async function updatePreview() {
    const subject = document.getElementById('subjectInput').value;
    const bodyHtml = document.getElementById('bodyInput').value;
    const previewSubject = document.getElementById('previewSubject');
    const previewBody = document.getElementById('previewBodyContainer');

    try {
        const data = await window.apiFetch('/api/templates/preview/', {
            method: 'POST',
            body: JSON.stringify({ subject, body_html: bodyHtml })
        });

        if (previewSubject) previewSubject.textContent = data.rendered_subject;
        if (previewBody) previewBody.innerHTML = data.rendered_body;
    } catch (err) {
        if (previewSubject) previewSubject.textContent = subject;
        if (previewBody) previewBody.innerHTML = bodyHtml;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const btnPreview = document.getElementById('btnPreview');
    const form = document.getElementById('campaignForm');
    const subjectInput = document.getElementById('subjectInput');
    const bodyInput = document.getElementById('bodyInput');
    const btnSend = document.getElementById('btnSendCampaign');

    if (btnPreview) {
        btnPreview.addEventListener('click', updatePreview);
    }

    if (subjectInput) subjectInput.addEventListener('input', updatePreview);
    if (bodyInput) bodyInput.addEventListener('input', updatePreview);

    // Initial Preview on Page Load
    updatePreview();

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const buyerIdsStr = document.getElementById('buyerIdsInput').value;
            const buyerIds = buyerIdsStr.split(',').map(i => parseInt(i.trim())).filter(i => !isNaN(i));

            if (buyerIds.length === 0) {
                alert('No buyer recipients selected.');
                return;
            }

            btnSend.disabled = true;
            btnSend.innerHTML = '🚀 Sending Pitch Emails...';

            try {
                const data = await window.apiFetch('/api/campaigns/', {
                    method: 'POST',
                    body: JSON.stringify({
                        subject: subjectInput.value,
                        body_html: bodyInput.value,
                        buyer_ids: buyerIds
                    })
                });

                if (data.id) {
                    window.location.href = `/campaigns/${data.id}/confirm/`;
                } else {
                    alert('Failed to send campaign.');
                    btnSend.disabled = false;
                    btnSend.innerHTML = '🚀 Send Campaign Now →';
                }
            } catch (err) {
                alert(`Campaign Error: ${err.message}`);
                btnSend.disabled = false;
                btnSend.innerHTML = '🚀 Send Campaign Now →';
            }
        });
    }
});
