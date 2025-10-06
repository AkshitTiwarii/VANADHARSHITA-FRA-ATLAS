import React, { useState, useEffect } from 'react';
import { X, Plus, Trash2, MapPin, AlertCircle, CheckCircle } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import axios from 'axios';

const ManageLocationsModal = ({ isOpen, onClose, onLocationAdded }) => {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    village: '',
    district: '',
    state: 'Maharashtra',
    latitude: '',
    longitude: ''
  });

  // Fetch locations on mount
  useEffect(() => {
    if (isOpen) {
      fetchLocations();
    }
  }, [isOpen]);

  const fetchLocations = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/monitoring/locations');
      setLocations(response.data.locations || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch locations');
      console.error('Error fetching locations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddLocation = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validate inputs
    if (!formData.village || !formData.district || !formData.state || 
        !formData.latitude || !formData.longitude) {
      setError('All fields are required');
      return;
    }

    const lat = parseFloat(formData.latitude);
    const lon = parseFloat(formData.longitude);

    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      setError('Invalid coordinates. Latitude: -90 to 90, Longitude: -180 to 180');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post('http://localhost:8000/api/monitoring/locations', {
        village: formData.village,
        district: formData.district,
        state: formData.state,
        latitude: lat,
        longitude: lon
      });

      setSuccess(`Successfully added ${formData.village}!`);
      setFormData({
        village: '',
        district: '',
        state: 'Maharashtra',
        latitude: '',
        longitude: ''
      });
      
      // Refresh locations
      await fetchLocations();
      
      // Notify parent
      if (onLocationAdded) {
        onLocationAdded();
      }

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add location');
      console.error('Error adding location:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteLocation = async (locationId, villageName) => {
    if (!window.confirm(`Are you sure you want to delete ${villageName}?`)) {
      return;
    }

    try {
      setLoading(true);
      await axios.delete(`http://localhost:8000/api/monitoring/locations/${locationId}`);
      setSuccess(`Deleted ${villageName}`);
      
      // Refresh locations
      await fetchLocations();
      
      // Notify parent
      if (onLocationAdded) {
        onLocationAdded();
      }

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete location');
      console.error('Error deleting location:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <MapPin className="w-6 h-6" />
            <div>
              <h2 className="text-2xl font-bold">Manage Monitoring Locations</h2>
              <p className="text-green-100 text-sm">Add or remove forest monitoring locations</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded-lg transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
          {/* Alerts */}
          {error && (
            <div className="m-6 mb-0 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="text-red-800">{error}</div>
            </div>
          )}

          {success && (
            <div className="m-6 mb-0 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div className="text-green-800">{success}</div>
            </div>
          )}

          {/* Add Location Form */}
          <div className="p-6">
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Plus className="w-5 h-5 text-green-600" />
                  Add New Monitoring Location
                </h3>

                <form onSubmit={handleAddLocation} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Village Name *
                    </label>
                    <input
                      type="text"
                      name="village"
                      value={formData.village}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="e.g., Bhamragad"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      District *
                    </label>
                    <input
                      type="text"
                      name="district"
                      value={formData.district}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="e.g., Gadchiroli"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      State *
                    </label>
                    <input
                      type="text"
                      name="state"
                      value={formData.state}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="e.g., Maharashtra"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Latitude * <span className="text-xs text-gray-500">(-90 to 90)</span>
                    </label>
                    <input
                      type="number"
                      step="0.0001"
                      name="latitude"
                      value={formData.latitude}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="e.g., 18.9217"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Longitude * <span className="text-xs text-gray-500">(-180 to 180)</span>
                    </label>
                    <input
                      type="number"
                      step="0.0001"
                      name="longitude"
                      value={formData.longitude}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="e.g., 77.0038"
                      required
                    />
                  </div>

                  <div className="flex items-end">
                    <Button 
                      type="submit" 
                      className="w-full bg-green-600 hover:bg-green-700"
                      disabled={loading}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      {loading ? 'Adding...' : 'Add Location'}
                    </Button>
                  </div>
                </form>

                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Tip:</strong> You can find GPS coordinates using Google Maps. Right-click on any location → Select "What's here?"
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Locations List */}
          <div className="px-6 pb-6">
            <h3 className="text-lg font-semibold mb-4">
              Current Monitoring Locations ({locations.length})
            </h3>

            {loading && locations.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Loading locations...
              </div>
            ) : locations.length === 0 ? (
              <Card>
                <CardContent className="py-8 text-center">
                  <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600">No monitoring locations added yet</p>
                  <p className="text-sm text-gray-500 mt-1">Add your first location using the form above</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {locations.map((location) => (
                  <Card key={location.id} className="hover:shadow-lg transition">
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-start gap-2 mb-2">
                            <MapPin className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                            <div>
                              <h4 className="font-semibold text-gray-900">{location.village}</h4>
                              <p className="text-sm text-gray-600">{location.district}, {location.state}</p>
                            </div>
                          </div>
                          
                          <div className="mt-3 space-y-1">
                            <div className="flex items-center text-xs text-gray-500">
                              <span className="font-medium w-20">Latitude:</span>
                              <span className="font-mono">{location.lat.toFixed(4)}°</span>
                            </div>
                            <div className="flex items-center text-xs text-gray-500">
                              <span className="font-medium w-20">Longitude:</span>
                              <span className="font-mono">{location.lon.toFixed(4)}°</span>
                            </div>
                            <div className="flex items-center text-xs text-gray-500">
                              <span className="font-medium w-20">Added:</span>
                              <span>{location.added_date}</span>
                            </div>
                          </div>
                        </div>

                        <button
                          onClick={() => handleDeleteLocation(location.id, location.village)}
                          className="text-red-600 hover:bg-red-50 p-2 rounded-lg transition"
                          disabled={loading}
                          title="Delete location"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 bg-gray-50 flex justify-end">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ManageLocationsModal;
