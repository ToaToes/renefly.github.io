let airportData = {};

// Add a dataReady flag to ensure you don’t search before data is available.
// search immediately after the fetch, but the fetch is asynchronous — 
// so when the input event first fires, the data might not have loaded yet, and airportData is still {}
let dataReady = false;

// Store currently selected valid airports
let selectedDeparture = null;
let selectedArrival = null;


fetch('airports.json')
  .then(response => response.json())
  .then(data => {
    airportData = data;
    
    dataReady = true; // Set the flag to true when data is loaded

  })
  .catch(err => console.error("Failed to load airports.json:", err));

function searchAirportsByCity(input) {
  if (!input || (input.trim() == "")) return [];

  const lowercaseInput = input.trim().toLowerCase();

  const matches = [];
  for (const code in airportData) {
    const airport = airportData[code];
    if (!airport.iata) continue;

    if (
      airport.iata.toLowerCase().includes(lowercaseInput) ||
      (airport.city && airport.city.toLowerCase().includes(lowercaseInput))
    ) {
      matches.push(airport);
    }
  }

  return matches;
}

function displayMatches(matches, containerId, inputId) {
  const container = document.getElementById(containerId);
  if (!matches || matches.length === 0) {
    container.innerHTML = '';
    container.style.display = 'none';
    return;
  }

  container.innerHTML = matches
    .slice(0, 10)
    .map(
      airport =>
        `<p class="airport-option" data-city="${airport.city}" data-iata="${airport.iata}" data-name="${airport.name}">
          <strong>${airport.city}</strong> — ${airport.iata} (${airport.name})
        </p>`
    )
    .join('');

  container.style.display = 'block';

  // Click handler for each option
  container.querySelectorAll('p.airport-option').forEach(option => {
    option.addEventListener('click', () => {
      const city = option.getAttribute('data-city');
      const iata = option.getAttribute('data-iata');
      document.getElementById(inputId).value = `${city} (${iata})`;
      container.innerHTML = '';
      container.style.display = 'none';

      // Save selected airport for validation
      if (inputId === 'departure') selectedDeparture = iata;
      if (inputId === 'arrival') selectedArrival = iata;

    });
  });
}

// Attach input listeners once
['departure', 'arrival'].forEach(inputId => {
  const input = document.getElementById(inputId);
  const containerId = inputId + 'Result';

  input.addEventListener('input', e => {
    if (!dataReady) return; // do nothing if data not loaded

    const value = e.target.value.trim();
    if (value === '') {
      document.getElementById(containerId).innerHTML = '';
      document.getElementById(containerId).style.display = 'none';

      // Clear selected airport
      if (inputId === 'departure') selectedDeparture = null;
      if (inputId === 'arrival') selectedArrival = null;
      return;
    }

    const matches = searchAirportsByCity(value);
    displayMatches(matches, containerId, inputId);
  });
});

// Optional: hide autocomplete when clicking outside
document.addEventListener('click', e => {
  ['departureResult', 'arrivalResult'].forEach(containerId => {
    const container = document.getElementById(containerId);
    const input = document.getElementById(containerId.replace('Result', ''));
    if (!container.contains(e.target) && !input.contains(e.target)) {
      container.innerHTML = '';
      container.style.display = 'none';
    }
  });
});

// Validate on form submission
document.getElementById('flightForm').addEventListener('submit', e => {
  if (!selectedDeparture || !selectedArrival) {
    e.preventDefault();
    alert("请从下拉列表选择有效的出发地和到达地！");
    return;
  }
});
