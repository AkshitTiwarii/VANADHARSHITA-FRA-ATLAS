import React from 'react';
import ReactDOM from 'react-dom/client';
import ForestAtlasGoogleMaps from './components/ForestAtlasGoogleMaps';
import './index.css';

// Standalone test page for Google Maps integration
// Run this with: npm start
// Then navigate to: http://localhost:3000

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ForestAtlasGoogleMaps />
  </React.StrictMode>
);
