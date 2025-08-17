import React, { useState, useEffect } from 'react';
import { Search, Filter, Navigation, Plus, Star, MapPin, Clock } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useSearchStore, useMapStore, useGeolocation } from '../lib/store';
import { restroomAPI, Restroom } from '../lib/api';
import toast from 'react-hot-toast';

const SearchPanel: React.FC = () => {
  const [showFilters, setShowFilters] = useState(false);
  const { getCurrentLocation } = useGeolocation();
  
  const {
    query,
    filters,
    recentSearches,
    setQuery,
    setFilters,
    addRecentSearch,
  } = useSearchStore();
  
  const {
    center,
    setSearchResults,
    setLoading,
  } = useMapStore();

  // Search restrooms query
  const { data: searchData, isLoading, error } = useQuery({
    queryKey: ['restrooms', 'search', center, filters, query],
    queryFn: async () => {
      if (!center[0] || !center[1]) return [];
      
      const params = {
        lat: center[1],
        lon: center[0],
        radius: filters.radius,
        min_rating: filters.minRating || undefined,
        wheelchair_accessible: filters.wheelchairAccessible || undefined,
        gender_neutral: filters.genderNeutral || undefined,
        baby_changing: filters.babyChanging || undefined,
        free_only: filters.freeOnly || undefined,
        limit: 50,
      };
      
      const response = await restroomAPI.search(params);
      return response.data;
    },
    enabled: !!center[0] && !!center[1],
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Update search results when data changes
  useEffect(() => {
    if (searchData) {
      setSearchResults(searchData);
    }
    setLoading(isLoading);
  }, [searchData, isLoading, setSearchResults, setLoading]);

  const handleGetLocation = async () => {
    try {
      const coords = await getCurrentLocation();
      toast.success('Location updated!');
      if (query) {
        addRecentSearch({ query, location: coords });
      }
    } catch (error) {
      toast.error('Could not get your location');
    }
  };

  const handleSearch = (searchQuery: string) => {
    setQuery(searchQuery);
    if (searchQuery && center[0] && center[1]) {
      addRecentSearch({ query: searchQuery, location: center });
    }
  };

  const RestroomCard: React.FC<{ restroom: Restroom }> = ({ restroom }) => (
    <div className="card-hover p-4 cursor-pointer">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h3 className="font-semibold text-primary-800 text-sm">
            {restroom.name || 'Public Restroom'}
          </h3>
          <p className="text-xs text-primary-600 truncate">
            {restroom.address || `${restroom.latitude.toFixed(4)}, ${restroom.longitude.toFixed(4)}`}
          </p>
        </div>
        {restroom.avg_overall > 0 && (
          <div className="flex items-center space-x-1 bg-psychedelic-purple text-white px-2 py-1 rounded-full text-xs">
            <Star className="w-3 h-3 fill-current" />
            <span>{restroom.avg_overall.toFixed(1)}</span>
          </div>
        )}
      </div>

      {/* Amenities */}
      <div className="flex flex-wrap gap-1 mb-2">
        {restroom.wheelchair_accessible === 'full' && (
          <span className="bg-primary-100 text-primary-700 px-2 py-1 rounded text-xs">♿ Accessible</span>
        )}
        {restroom.baby_changing && (
          <span className="bg-primary-100 text-primary-700 px-2 py-1 rounded text-xs">👶 Baby changing</span>
        )}
        {restroom.gender_neutral && (
          <span className="bg-primary-100 text-primary-700 px-2 py-1 rounded text-xs">🚻 Gender neutral</span>
        )}
        {!restroom.requires_fee && (
          <span className="bg-success/10 text-success px-2 py-1 rounded text-xs">Free</span>
        )}
      </div>

      {/* Distance and reviews */}
      <div className="flex items-center justify-between text-xs text-primary-600">
        <div className="flex items-center space-x-1">
          <MapPin className="w-3 h-3" />
          <span>{restroom.distance ? `${(restroom.distance / 1000).toFixed(1)} km` : 'Unknown distance'}</span>
        </div>
        <span>{restroom.review_count} reviews</span>
      </div>

      {restroom.temporarily_closed && (
        <div className="mt-2 text-xs text-warning font-medium">
          ⚠️ Temporarily closed
        </div>
      )}
    </div>
  );

  return (
    <div className="w-96 bg-white shadow-lg border-r border-primary-200 flex flex-col h-full">
      {/* Search Header */}
      <div className="p-6 border-b border-primary-200">
        <h1 className="text-2xl font-display font-bold text-primary-800 mb-4">
          Find Restrooms
        </h1>
        
        {/* Search Bar */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search location..."
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            className="input-primary pl-10"
          />
        </div>
        
        {/* Action Buttons */}
        <div className="flex space-x-2 mb-4">
          <button
            onClick={handleGetLocation}
            className="btn-primary flex items-center space-x-2 flex-1"
          >
            <Navigation className="w-4 h-4" />
            <span>Use My Location</span>
          </button>
          
          <button 
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-secondary flex items-center space-x-2 ${showFilters ? 'bg-primary-100' : ''}`}
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="space-y-4 p-4 bg-primary-50 rounded-lg">
            <div>
              <label className="block text-sm font-medium text-primary-700 mb-2">
                Minimum Rating
              </label>
              <select
                value={filters.minRating || ''}
                onChange={(e) => setFilters({ minRating: e.target.value ? Number(e.target.value) : null })}
                className="input-primary text-sm"
              >
                <option value="">Any rating</option>
                <option value="4">4+ stars</option>
                <option value="3">3+ stars</option>
                <option value="2">2+ stars</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-primary-700 mb-2">
                Search Radius
              </label>
              <select
                value={filters.radius}
                onChange={(e) => setFilters({ radius: Number(e.target.value) })}
                className="input-primary text-sm"
              >
                <option value="1000">1 km</option>
                <option value="2000">2 km</option>
                <option value="5000">5 km</option>
                <option value="10000">10 km</option>
                <option value="25000">25 km</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.wheelchairAccessible || false}
                  onChange={(e) => setFilters({ wheelchairAccessible: e.target.checked || null })}
                  className="rounded border-primary-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-primary-700">Wheelchair accessible</span>
              </label>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.genderNeutral || false}
                  onChange={(e) => setFilters({ genderNeutral: e.target.checked || null })}
                  className="rounded border-primary-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-primary-700">Gender neutral</span>
              </label>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.babyChanging || false}
                  onChange={(e) => setFilters({ babyChanging: e.target.checked || null })}
                  className="rounded border-primary-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-primary-700">Baby changing station</span>
              </label>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.freeOnly || false}
                  onChange={(e) => setFilters({ freeOnly: e.target.checked || null })}
                  className="rounded border-primary-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-primary-700">Free only</span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-6 text-center">
            <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-primary-600">Searching for restrooms...</p>
          </div>
        ) : error ? (
          <div className="p-6 text-center">
            <p className="text-error">Error loading restrooms</p>
          </div>
        ) : searchData && searchData.length > 0 ? (
          <div className="p-4 space-y-3">
            {searchData.map((restroom) => (
              <RestroomCard key={restroom.id} restroom={restroom} />
            ))}
          </div>
        ) : (
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold text-primary-700 mb-2">
              Start Your Search
            </h3>
            <p className="text-primary-600 text-sm">
              Use your location or search for a place to find nearby restrooms
            </p>
          </div>
        )}
      </div>

      {/* Add Restroom Button */}
      <div className="p-6 border-t border-primary-200">
        <button className="btn-psychedelic w-full flex items-center justify-center space-x-2">
          <Plus className="w-5 h-5" />
          <span>Add New Restroom</span>
        </button>
      </div>
    </div>
  );
};

export default SearchPanel;
