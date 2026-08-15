import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import FleetDashboard from './pages/FleetDashboard';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Default redirect to fleet while the rest of the app is wired in */}
        <Route path="/" element={<Navigate to="/fleet" replace />} />
        <Route path="/fleet" element={<FleetDashboard />} />
      </Routes>
    </BrowserRouter>
  );
}
