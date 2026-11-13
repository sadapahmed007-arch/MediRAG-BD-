import { Routes, Route } from 'react-router-dom';
import Layout from './layouts/Layout';
import Ask from './pages/Ask';
import Answer from './pages/Answer';
import Explore from './pages/Explore';
import HowItWorks from './pages/HowItWorks';
import Research from './pages/Research';
import About from './pages/About';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Ask />} />
        <Route path="answer" element={<Answer />} />
        <Route path="explore" element={<Explore />} />
        <Route path="how-it-works" element={<HowItWorks />} />
        <Route path="research" element={<Research />} />
        <Route path="about" element={<About />} />
      </Route>
    </Routes>
  );
}
