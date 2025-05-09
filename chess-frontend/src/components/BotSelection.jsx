import React, { useState } from "react";
import "../styles/BotSelection.css";
import { useNavigate } from "react-router-dom";

const bots = [
  {
    name: "Wyatt",
    image: "/static/images/avatars/wyatt.png",
    description: "Moves randomly. Always plays white.",
  },
  {
    name: "Moose",
    image: "/static/images/avatars/moose.png",
    description: "Moves randomly. Always plays black",
  },
];

const BotSelection = () => {
  const [selectedBot, setSelectedBot] = useState(null);
  const navigate = useNavigate();

  const handlePlay = () => {
    if (selectedBot) {
      navigate(`/play?bot=${selectedBot}`);
    }
  };

  return (
    <div className="bot-selection-container">
      <h1>Select Your Opponent</h1>
      <button onClick={handlePlay} disabled={!selectedBot}>
        Play
      </button>
      <div className="bot-grid">
        {bots.map((bot) => (
          <div
            key={bot.name}
            className={`bot-card ${selectedBot === bot.name ? "selected" : ""}`}
            onClick={() => setSelectedBot(bot.name)}
            title={bot.description}
          >
            <img src={bot.image} alt={bot.name} />
            <span>{bot.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BotSelection;
