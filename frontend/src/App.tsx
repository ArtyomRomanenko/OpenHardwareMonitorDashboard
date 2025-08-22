import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Metrics from './pages/Metrics';
import Insights from './pages/Insights';
import SystemInfo from './pages/SystemInfo';

function App() {
  return (
    <div className="App">
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/metrics" element={<Metrics />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/system" element={<SystemInfo />} />
        </Routes>
      </Layout>
    </div>
  );
}

export default App;
