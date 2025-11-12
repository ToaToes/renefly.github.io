let airportData = {};

// Add a dataReady flag to ensure you don’t search before data is available.
// search immediately after the fetch, but the fetch is asynchronous — 
// so when the input event first fires, the data might not have loaded yet, and airportData is still {}
let dataReady = false;


fetch('airports.json')
  .then(response => response.json())
  .then(data => {
    airportData = data;
    dataReady = true; // Set the flag to true when data is loaded
  });

function searchAirportsByCity(input) {
  if (!input || (input.trim() == "")) return [];

  const lowercaseInput = input.trim().toLowerCase();

  const matches = [];
  for (const code in airportData) {
    const airport = airportData[code];
    //sort out all empty IATA codes
    if (airport.iata && airport.iata.toLowerCase().includes(lowercaseInput) && (airport.iata !== "")) {
      matches.push(airport);
    }
    else if (airport.city && airport.city.toLowerCase().includes(lowercaseInput) && (airport.iata !== "")) {
      matches.push(airport);
    }
  }
  return matches;
}

function displayMatches(matches, containerId, inputId) {
  const container = document.getElementById(containerId);
  if (matches.length === 0) {
    container.innerHTML = '<p>No matches found</p>';
  } else {
    container.innerHTML = matches
      .slice(0, 10) // limit results to 10
      .map(
        (airport) =>
            `<p class="airport-option" data-city="${airport.city}" data-iata="${airport.iata}" data-name="${airport.name}">
                <strong>${airport.city}</strong> — ${airport.iata} (${airport.name})
            </p>`

      )
      .join('');

      // Add click event listeners to each airport option
      const options = container.querySelectorAll('p');
      options.forEach(option => {
      option.addEventListener('click', () => {
        const city = option.getAttribute('data-city');
        const iata = option.getAttribute('data-iata');
        // You can choose what to insert in the input:
        document.getElementById(inputId).value = `${city} (${iata})`;
        container.innerHTML = ''; // Clear suggestions after selection
      });
    });
  }
}

document.getElementById('departure').addEventListener('input', (e) => {
  if (!dataReady) return; // Do nothing if data is not ready
  const matches = searchAirportsByCity(e.target.value);
  displayMatches(matches, 'departureResult', 'departure');
});

document.getElementById('arrival').addEventListener('input', (e) => {
  if (!dataReady) return; // Do nothing if data is not ready
  const matches = searchAirportsByCity(e.target.value);
  displayMatches(matches, 'arrivalResult', 'arrival');
});
