import React from "react";
import { Routes, Route } from "react-router-dom";
import BotSelection from "./components/BotSelection";
import PlayPage from "./components/PlayPage";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<BotSelection />} />
      <Route path="/play" element={<PlayPage />} />
    </Routes>
  );
};

export default App;