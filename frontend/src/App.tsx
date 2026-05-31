import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { TeamsList } from './pages/TeamsList';
import { TeamDetail } from './pages/TeamDetail';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<TeamsList />} />
        <Route path="/teams/:teamId" element={<TeamDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;