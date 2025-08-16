document.getElementById('micButton').addEventListener('click', () => {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.start();

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById('symptoms').value = transcript;
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
  };
});

document.getElementById('symptomForm').addEventListener('submit', function (e) {
  e.preventDefault();
  const symptoms = document.getElementById('symptoms').value.split(',').map(s => s.trim());

  fetch('/recommend-doctor', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symptoms }),
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById('specialization').textContent = data.recommendedSpecialization || 'No specialization found';
    })
    .catch(err => console.error('Error:', err));
});
