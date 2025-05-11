import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

const PlayPage = () => {
  const [loading, setLoading] = useState(true);
  const [gameId, setGameId] = useState(null);
  const [error, setError] = useState(null);

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const selectedBot = params.get("bot");

  useEffect(() => {
    if (!selectedBot) {
      setError("No bot selected.");
      setLoading(false);
      return;
    }

    fetch("/api/start-game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bot: selectedBot }),
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to start game");
        return res.json();
      })
      .then(data => {
        setGameId(data.game_id); // Adjust according to your backend
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError("Error starting game");
        setLoading(false);
      });
  }, [selectedBot]);

  if (loading) return <p>Starting game with {selectedBot}...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div>
      <h1>Game vs {selectedBot} started!</h1>
      <p>Game ID: {gameId}</p>
      {/* Render your game board component here later */}
    </div>
  );
};

export default PlayPage;
