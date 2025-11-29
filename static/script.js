async function addComments() {
    const input = document.getElementById('input').value;
    const output = document.getElementById('output');
    const button = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');

    if (!input.trim()) {
        alert('Please enter some code first!');
        return;
    }

    // Reset and prepare UI
    output.value = '';
    button.disabled = true;
    loading.classList.remove('hidden');

    try {
        const response = await fetch('/add-comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: input })
        });

        if (!response.ok) {
            throw new Error('Failed to generate comments');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            output.value += chunk;
            output.scrollTop = output.scrollHeight;
        }

    } catch (error) {
        console.error('Error:', error);
        output.value = 'Error generating comments. Please try again.';
    } finally {
        button.disabled = false;
        loading.classList.add('hidden');
    }
}

// Allow Enter key in textarea (Ctrl+Enter to submit)
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('input').addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            addComments();
        }
    });
});