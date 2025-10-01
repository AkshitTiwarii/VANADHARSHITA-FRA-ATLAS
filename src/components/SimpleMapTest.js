import React, { useEffect, useRef, useState } from 'react';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { fromLonLat } from 'ol/proj';
import 'ol/ol.css';

const SimpleMapTest = () => {
  const mapRef = useRef();
  const mapInstance = useRef();
  const [mapStatus, setMapStatus] = useState('initializing');

  useEffect(() => {
    if (!mapRef.current) {
      setMapStatus('no container');
      return;
    }

    try {
      console.log('Creating simple test map...');
      
      const map = new Map({
        target: mapRef.current,
        layers: [
          new TileLayer({
            source: new OSM()
          })
        ],
        view: new View({
          center: fromLonLat([78.9629, 20.5937]),
          zoom: 6
        })
      });

      mapInstance.current = map;
      setMapStatus('loaded');
      console.log('Test map created successfully');

    } catch (error) {
      console.error('Test map failed:', error);
      setMapStatus('failed');
    }

    return () => {
      if (mapInstance.current) {
        mapInstance.current.setTarget(null);
      }
    };
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">OpenLayers Test Map</h2>
      <p className="mb-4">Status: {mapStatus}</p>
      <div 
        ref={mapRef}
        style={{
          width: '100%',
          height: '400px',
          border: '1px solid #ccc',
          backgroundColor: '#f0f0f0'
        }}
      />
    </div>
  );
};

export default SimpleMapTest;