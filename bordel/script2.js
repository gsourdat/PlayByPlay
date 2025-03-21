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
            
            const formattedStart = `${startDate}T00%3A00%3A00`;
            const formattedEnd = `${startDate}T23%3A59%3A59`;
            
            const url = `http://127.0.0.1:5000/matchesBetween?starting_time=${encodeURIComponent(formattedStart)}&ending_time=${encodeURIComponent(formattedEnd)}`;
            document.getElementById("matches-container").innerHTML = "Chargement...";
            
            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Erreur HTTP : ${response.status}`);
                    }
                    return response.text();
                })
                .then(text => {
                    try {
                        const data = JSON.parse(text);
                        const container = document.getElementById("matches-container");
                        container.innerHTML = "";
                        
                        if (Array.isArray(data) && data.length > 0) {
                            data.forEach(match => {
                                const card = document.createElement("div");
                                card.className = "match-card";
                                card.style.backgroundColor = match.status === "finished" ? "#f8d7da" : "#ffffff";
                                
                                const team1 = match.opponents[0]?.opponent.name || "Équipe 1";
                                const team2 = match.opponents[1]?.opponent.name || "Équipe 2";
                                const logo1 = match.opponents[0]?.opponent.image_url || "default_logo.png";
                                const logo2 = match.opponents[1]?.opponent.image_url || "default_logo.png";
                                const leagueLogo = match.league.image_url || "default_league.png";
                                
                                const score = match.results.length > 1 ? `${match.results[0].score} - ${match.results[1].score}` : "En attente";
                                
                                card.innerHTML = `
                                    <div class="match-header">
                                        <img src="${leagueLogo}" class="league-logo" alt="${match.league.name}">
                                        <h2>${match.league.name} - ${match.serie.name}</h2>
                                    </div>
                                    <div class="match-info">
                                        <img src="${logo1}" class="team-logo" alt="${team1}">
                                        <div class="match-details">
                                            <h2>${team1} vs ${team2}</h2>
                                            <p><strong>Statut:</strong> ${match.status}</p>
                                            <p><strong>Début:</strong> ${new Date(match.begin_at).toLocaleString()}</p>
                                            <div class="score-wrapper">
                                                <div class="score-card" onclick="revealScore(event)">
                                                    <img src="images/eyeBarre.png" class="eye-image" alt="Œil barré">
                                                </div>
                                                <p class="score">${score}</p>  <!-- Le score réel du match -->
                                            </div>
                                        </div>
                                        <img src="${logo2}" class="team-logo" alt="${team2}">
                                    </div>


                                    ${match.status === "in_progress" ? '<div class="live-sign">EN DIRECT</div>' : ''}
                                `;



                                container.appendChild(card);
                            });
                        } else {
                            container.innerHTML = "<p>Aucun match trouvé.</p>";
                        }
                    } catch (error) {
                        console.error("Erreur lors du parsing JSON :", error, "\nRéponse brute :", text);
                        document.getElementById("matches-container").innerHTML = "<p>Erreur de chargement des matchs.</p>";
                    }
                })
                .catch(error => {
                    console.error("Erreur lors de la récupération des matchs :", error);
                    document.getElementById("matches-container").innerHTML = "<p>Erreur de chargement des matchs.</p>";
                });
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
        });

