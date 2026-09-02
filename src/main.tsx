import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./index.css";
import ControlCenter from "./pages/ControlCenter";
import QueryTransactions from "./pages/QueryTransactions";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/control-center" replace />} />
        <Route path="/control-center" element={<ControlCenter />} />
        <Route path="/query" element={<QueryTransactions />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
