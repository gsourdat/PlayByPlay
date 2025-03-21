
document.addEventListener("DOMContentLoaded", function () {
    const datePicker = document.getElementById("datePicker");

    // Vérifier si une date est déjà stockée
    if (localStorage.getItem("selectedDate")) {
        datePicker.value = localStorage.getItem("selectedDate");
    }

    // Sauvegarder la nouvelle valeur dans localStorage
    datePicker.addEventListener("change", function () {
        localStorage.setItem("selectedDate", datePicker.value);
    });
});
let currentDate = new Date();

        function updateDatePicker() {
            const startDate = currentDate.toISOString().split("T")[0];
            document.getElementById("start-date").value = startDate;
            fetchMatches();
        }

        function fetchMatches() {
            const startDate = document.getElementById("start-date").value;
            if (!startDate) {
                alert("Veuillez sélectionner le jour des matchs.");
                return;
            }
            
            const formattedStart = `${startDate} 00:00:00`;
            const formattedEnd = `${startDate} 23:59:59`;
            
            const url = `http://127.0.0.1:5000/matchesBetween?starting_time=${encodeURIComponent(formattedStart)}&ending_time=${encodeURIComponent(formattedEnd)}`;
            document.getElementById("matches-container").innerHTML = "Chargement...";
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById("matches-container");
                    container.innerHTML = "";
                    console.log(data);
                    if (Array.isArray(data) && data.length > 0) {
                        data.forEach(match => {
                            const card = document.createElement("div");
                            card.className = "match-card";
                            card.setAttribute("data-match-id", match.match_id);
                            card.onclick = (event) => goToMatch(event, match.match_id);
                            
                            card.innerHTML = `
                                <div class="match-header">
                                    ${match.status === "in_progress" ? '<div class="live-sign">EN DIRECT</div>' : ''}
                                    <div class="league-container">
                                        <img src="${match.league_logo || 'default_league.png'}" class="league-logo" alt="${match.league_name}">
                                        <h2>${match.league_name}</h2>
                                    </div>
                                </div>

                                <div class="match-info">
                                    <img src="${match.team1_logo || 'default_logo.png'}" class="team-logo" alt="${match.team1_name}">
                                    <div class="match-details">
                                        <h2>${match.team1_name} vs ${match.team2_name}</h2>
                                        <p><strong>Statut:</strong> ${match.status}</p>
                                        <p><strong>Début:</strong> ${new Date(match.start_time).toLocaleString()}</p>
                                        <div class="score-wrapper">
                                            <p class="score">${match.score_team1} - ${match.score_team2}</p>
                                        </div>
                                    </div>
                                    <img src="${match.team2_logo || 'default_logo.png'}" class="team-logo" alt="${match.team2_name}">
                                </div>
                                
                            `;
        
                            container.appendChild(card);
                        });
                    } else {
                        container.innerHTML = "<p>Aucun match trouvé.</p>";
                    }
                            // Restaurer la position de défilement après le rechargement
                    if (localStorage.getItem("scrollPosition")) {
                        window.scrollTo(0, localStorage.getItem("scrollPosition"));
                    }
                })
                .catch(error => {
                    console.error("Erreur lors de la récupération des matchs :", error);
                    document.getElementById("matches-container").innerHTML = "<p>Erreur de chargement des matchs.</p>";
                });
        }
        
        function goToMatch(event, matchId) {
            event.stopPropagation(); // Empêche les événements imbriqués de se déclencher
            //window.location.href = `match.html?id=${matchId}`;
            window.location.href = `/match/${matchId}`;
        }
        

        function changeDate(offset) {
            currentDate.setDate(currentDate.getDate() + offset);
            updateDatePicker();
        }
        
        // Fonction pour gérer le clic sur la carte grisée et révéler le score
        function revealScore(event) {
            const card = event.target.closest(".score-card");
            const score = card.nextElementSibling; // Le score est juste après la carte grisée
            
            // Révéler le score
            score.classList.add("revealed");
            
            // Cacher la carte grisée
            card.style.display = "none";
        }

        document.addEventListener("DOMContentLoaded", () => {
            updateDatePicker();
            const today = new Date().toISOString().split("T")[0];
            document.getElementById("start-date").value = today;
            fetchMatches();

            // Initialiser Socket.IO
            var socket = io.connect('http://localhost:5000');
            // Restaurer la position de défilement après le rechargement
            if (localStorage.getItem("scrollPosition")) {
                window.scrollTo(0, localStorage.getItem("scrollPosition"));
            }

            // Écouter l'événement 'update_matches'
            socket.on('update_matches', function(data) {
                console.log(data.message);
                // Enregistrer la position de défilement avant le rechargement
                localStorage.setItem("scrollPosition", window.scrollY);
                fetchMatches(); // Mettre à jour l'affichage des matchs
            });
        });

