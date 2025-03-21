let gamesData = [];
const matchContainer = document.querySelector('.match-container');
const matchId = matchContainer.getAttribute('data-match-id');
            function fetchMatchDetails() {
                console.log("matchId : ");
                console.log(matchId);
                if (!matchId) {
                    document.getElementById("match-container").innerHTML = "<p style='color: red;'>ID du match invalide.</p>";
                    return;
                }
                
                const url = `http://127.0.0.1:5000/matchDetail?id=${matchId}`;
                console.log("url : ");
                console.log(url);
                fetch(url)
                    .then(response => response.json())
                    .then(match => {
                        document.getElementById("match-container").innerHTML = `
                            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px;">
                                <img src="${match.team1_logo}" class="team-logo" alt="${match.team1_name}">    
                                <h2 style="font-size: 2em; font-weight: bold; color: #00A3FF; white-space: nowrap;">${match.team1_name} - ${match.team2_name}</h2>
                                <img src="${match.team2_logo}" class="team-logo" alt="${match.team2_name}">
                            </div>
                            <p style="font-size: 1.2em;"><strong>Statut:</strong> ${match.status}</p>
                            <p style="font-size: 1.2em;"><strong>Date:</strong> ${new Date(match.start_time).toLocaleString()}</p>
                            <p style="font-size: 2em; font-weight: bold; color: #A0A0A0;">${match.score_team1} - ${match.score_team2}</p>
                        `;
                        
                        const team1Composition = document.getElementById("team1-composition");
                        const team2Composition = document.getElementById("team2-composition");

                        match.team1_players.forEach(player => {
                            team1Composition.innerHTML += `
                                <div class="player-card">
                                    <img src="${player.photo || 'static/images/none-player.png'}" class="player-image" alt="${player.name}">
                                    <div class="info">
                                        <p class="summoner-name">${player.summoner_name}</p>
                                        <p class="player-name">${player.name}</p>
                                    </div>
                                    <img src="../static/images/${player.role}.png"  class="role" alt="${player.role}">
                                </div>
                            `;
                        });
                        
                        match.team2_players.forEach(player => {
                            team2Composition.innerHTML += `
                                <div class="player-card">
                                    <img src="${player.photo || 'static/images/none-player.png'}" class="player-image" alt="${player.name}">
                                    <div class="info">
                                        <p class="summoner-name">${player.summoner_name}</p>
                                        <p class="player-name">${player.name}</p>
                                    </div>
                                    <img src="../static/images/${player.role}.png" class="role" alt="${player.role}">
                                </div>
                            `;
                        });

                        fetchMatchGames(matchId);
                    })
                    .catch(error => {
                        console.error("Erreur lors de la récupération du match:", error);
                        document.getElementById("match-container").innerHTML = "<p style='color: red;'>Erreur de chargement des détails du match.</p>";
                    });
            }

            function fetchMatchGames(matchId) {
                const url = `http://127.0.0.1:5000/matchGames?match_id=${matchId}`;
                fetch(url)
                    .then(response => response.json())
                    .then(games => {
                        gamesData = games;
                        const gameSelection = document.getElementById("game-selection");
                        games.forEach((game, index) => {
                            const button = document.createElement("button");
                            button.className = "game-button";
                            button.textContent = `${game.game_number}`;
                            button.onclick = () => {
                                displayGameDetails(index);
                                setActiveButton(button);
                            };
                            gameSelection.appendChild(button);
                        });

                        if (games.length > 0) {
                            displayGameDetails(0);
                            setActiveButton(gameSelection.children[0]);
                        }
                    })
                    .catch(error => {
                        console.error("Erreur lors de la récupération des games:", error);
                        document.getElementById("game-details").innerHTML = "<p style='color: red;'>Erreur de chargement des games.</p>";
                    });
            }

            function setActiveButton(activeButton) {
                const buttons = document.querySelectorAll(".game-button");
                buttons.forEach(button => {
                    button.classList.remove("active");
                });
                activeButton.classList.add("active");
            }

            function displayGameDetails(index) {
                const gameDetails = document.getElementById("game-details");
                const selectedGame = gamesData[index];

                if (selectedGame) {
                    let team1Players = '';
                    let team2Players = '';

                    selectedGame.team1_players.forEach(player => {
                        team1Players += `
                            <div class="player-game-card" width="100%">
                                <img src="../static/images/champions/${player.champion}.png" class="champion-image" alt="${player.champion}"  title="${player.champion}" height=48>
                                <div class="info">
                                    <p class="summoner-name">${player.summoner_name}</p>
                                </div>
                            </div>
                        `;
                    });

                    selectedGame.team2_players.forEach(player => {
                        team2Players += `
                            <div class="player-game-card" width="100%">
                                <img src="../static/images/champions/${player.champion}.png" class="champion-image" alt="${player.champion}"  title="${player.champion}" height=48>
                                <div class="info">
                                    <p class="summoner-name">${player.summoner_name}</p>
                                </div>
                            </div>
                        `;
                    });

                    gameDetails.innerHTML = `
                        <h3>Game ${selectedGame.game_number}</h3>
                        <h3>${selectedGame.score_team1} - ${selectedGame.score_team2}</h3>
                        <div class="team-details" style="display: flex; justify-content: space-between;">
                            <div class="team1-players" style="flex: 1;">
                                <img src="${selectedGame.team1_logo}" class="lil-team-logo" alt="${selectedGame.team1_name}">
                                <div style="display: flex; flex-wrap: wrap;">
                                    ${team1Players}
                                </div>
                            </div>
                            <div class="team2-players" style="flex: 1;">
                                <img src="${selectedGame.team2_logo}" class="lil-team-logo" alt="${selectedGame.team2_name}">
                                <div style="display: flex; flex-wrap: wrap;">
                                    ${team2Players}
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    gameDetails.innerHTML = "<p>Aucune game disponible.</p>";
                }
            }

            function goBack() {
                window.history.back();
            }

            document.addEventListener("DOMContentLoaded", fetchMatchDetails);