import React, { useCallback, useRef, useState } from 'react';
import Map, { Marker, Popup, NavigationControl, GeolocateControl } from 'react-map-gl';
import { useMapStore, useSearchStore } from '../lib/store';
import { Restroom } from '../lib/api';
import PuperLogo from './PuperLogo';
import { Star, Navigation, Clock, DollarSign, Accessibility } from 'lucide-react';
import 'mapbox-gl/dist/mapbox-gl.css';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || 'pk.eyJ1IjoicHVwZXIiLCJhIjoiY2xkZjEyM3g0MDAwMDNxbzJxbzJxbzJxbyJ9.demo';

interface MapComponentProps {
  className?: string;
}

const MapComponent: React.FC<MapComponentProps> = ({ className = '' }) => {
  const mapRef = useRef<any>();
  const [selectedRestroom, setSelectedRestroom] = useState<Restroom | null>(null);
  
  const { center, zoom, searchResults, setCenter, setZoom } = useMapStore();
  const { query } = useSearchStore();

  const onMapLoad = useCallback(() => {
    // Map loaded successfully
  }, []);

  const onMarkerClick = useCallback((restroom: Restroom) => {
    setSelectedRestroom(restroom);
    setCenter([restroom.longitude, restroom.latitude]);
  }, [setCenter]);

  const onPopupClose = useCallback(() => {
    setSelectedRestroom(null);
  }, []);

  // Custom marker component
  const RestroomMarker: React.FC<{ restroom: Restroom }> = ({ restroom }) => (
    <Marker
      longitude={restroom.longitude}
      latitude={restroom.latitude}
      anchor="bottom"
      onClick={() => onMarkerClick(restroom)}
    >
      <div className="relative cursor-pointer transform hover:scale-110 transition-transform">
        <div className="w-8 h-8 bg-primary-600 rounded-full border-2 border-white shadow-lg flex items-center justify-center">
          <PuperLogo size="sm" showText={false} className="w-6 h-6" />
        </div>
        {restroom.avg_overall > 0 && (
          <div className="absolute -top-2 -right-2 bg-psychedelic-purple text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
            {restroom.avg_overall.toFixed(1)}
          </div>
        )}
      </div>
    </Marker>
  );

  // Popup component for restroom details
  const RestroomPopup: React.FC<{ restroom: Restroom }> = ({ restroom }) => (
    <Popup
      longitude={restroom.longitude}
      latitude={restroom.latitude}
      anchor="top"
      onClose={onPopupClose}
      closeButton={true}
      closeOnClick={false}
      className="restroom-popup"
    >
      <div className="p-4 min-w-[280px]">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="font-semibold text-primary-800 text-lg">
              {restroom.name || 'Public Restroom'}
            </h3>
            <p className="text-sm text-primary-600">
              {restroom.address || `${restroom.latitude.toFixed(4)}, ${restroom.longitude.toFixed(4)}`}
            </p>
          </div>
          {restroom.avg_overall > 0 && (
            <div className="flex items-center space-x-1 bg-psychedelic-purple text-white px-2 py-1 rounded-full text-sm">
              <Star className="w-3 h-3 fill-current" />
              <span>{restroom.avg_overall.toFixed(1)}</span>
            </div>
          )}
        </div>

        {restroom.description && (
          <p className="text-sm text-primary-700 mb-3">{restroom.description}</p>
        )}

        {/* Amenities */}
        <div className="grid grid-cols-2 gap-2 mb-3">
          {restroom.wheelchair_accessible === 'full' && (
            <div className="flex items-center space-x-1 text-xs text-primary-600">
              <Accessibility className="w-3 h-3" />
              <span>Accessible</span>
            </div>
          )}
          {restroom.requires_fee && (
            <div className="flex items-center space-x-1 text-xs text-primary-600">
              <DollarSign className="w-3 h-3" />
              <span>{restroom.fee_amount ? `$${restroom.fee_amount}` : 'Fee required'}</span>
            </div>
          )}
          {restroom.baby_changing && (
            <div className="flex items-center space-x-1 text-xs text-primary-600">
              <span>👶</span>
              <span>Baby changing</span>
            </div>
          )}
          {restroom.gender_neutral && (
            <div className="flex items-center space-x-1 text-xs text-primary-600">
              <span>🚻</span>
              <span>Gender neutral</span>
            </div>
          )}
        </div>

        {/* Distance */}
        {restroom.distance && (
          <div className="flex items-center space-x-1 text-xs text-primary-600 mb-3">
            <Navigation className="w-3 h-3" />
            <span>{(restroom.distance / 1000).toFixed(1)} km away</span>
          </div>
        )}

        {/* Reviews count */}
        <div className="flex items-center justify-between text-xs text-primary-600">
          <span>{restroom.review_count} reviews</span>
          {restroom.temporarily_closed && (
            <span className="text-warning font-medium">Temporarily closed</span>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex space-x-2 mt-3">
          <button className="btn-primary text-xs py-1 px-3 flex-1">
            View Details
          </button>
          <button className="btn-secondary text-xs py-1 px-3 flex-1">
            Get Directions
          </button>
        </div>
      </div>
    </Popup>
  );

  return (
    <div className={`relative ${className}`}>
      <Map
        ref={mapRef}
        mapboxAccessToken={MAPBOX_TOKEN}
        initialViewState={{
          longitude: center[0],
          latitude: center[1],
          zoom: zoom,
        }}
        style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/streets-v12"
        onLoad={onMapLoad}
        onMove={(evt) => {
          setCenter([evt.viewState.longitude, evt.viewState.latitude]);
          setZoom(evt.viewState.zoom);
        }}
        interactiveLayerIds={[]}
      >
        {/* Navigation Controls */}
        <NavigationControl position="top-right" />
        
        {/* Geolocation Control */}
        <GeolocateControl
          position="top-right"
          trackUserLocation={true}
          showUserHeading={true}
        />

        {/* Restroom Markers */}
        {searchResults.map((restroom) => (
          <RestroomMarker key={restroom.id} restroom={restroom} />
        ))}

        {/* Selected Restroom Popup */}
        {selectedRestroom && (
          <RestroomPopup restroom={selectedRestroom} />
        )}
      </Map>

      {/* Map overlay for search status */}
      {query && searchResults.length === 0 && (
        <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-3">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-sm text-primary-700">Searching for restrooms...</span>
          </div>
        </div>
      )}

      {/* Results count */}
      {searchResults.length > 0 && (
        <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-3">
          <span className="text-sm text-primary-700 font-medium">
            Found {searchResults.length} restroom{searchResults.length !== 1 ? 's' : ''}
          </span>
        </div>
      )}
    </div>
  );
};

export default MapComponent;
