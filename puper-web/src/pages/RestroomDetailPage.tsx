import React from 'react';

import { format } from 'date-fns';
import {
  Accessibility,
  ArrowLeft,
  Baby,
  DollarSign,
  Heart,
  MapPin,
  Navigation,
  Share2,
  Star,
  Users,
} from 'lucide-react';
import {
  Link,
  useParams,
} from 'react-router-dom';

import { useQuery } from '@tanstack/react-query';

// import ReviewSystem from '../components/ReviewSystem';
import { restroomAPI } from '../lib/api';

const RestroomDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const { data: restroom, isLoading, error } = useQuery({
    queryKey: ['restroom', id],
    queryFn: async () => {
      if (!id) throw new Error('No restroom ID provided');
      const response = await restroomAPI.getById(id);
      return response.data;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="text-center py-12">
          <div className="w-12 h-12 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-primary-600">Loading restroom details...</p>
        </div>
      </div>
    );
  }

  if (error || !restroom) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="card text-center py-12">
          <h1 className="text-2xl font-display font-bold text-primary-800 mb-4">
            Restroom Not Found
          </h1>
          <p className="text-primary-600 mb-6">
            The restroom you're looking for doesn't exist or has been removed.
          </p>
          <Link to="/" className="btn-primary">
            Back to Map
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <Link
          to="/"
          className="p-2 rounded-lg hover:bg-primary-100 transition-colors"
          aria-label="Back to map"
        >
          <ArrowLeft className="w-5 h-5 text-primary-600" />
        </Link>
        <h1 className="text-3xl font-display font-bold text-primary-800">
          {restroom.name || 'Public Restroom'}
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info Card */}
          <div className="card">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <MapPin className="w-5 h-5 text-primary-600" />
                  <span className="text-primary-700">
                    {restroom.address || `${restroom.latitude.toFixed(4)}, ${restroom.longitude.toFixed(4)}`}
                  </span>
                </div>
                {restroom.city && restroom.country && (
                  <p className="text-sm text-primary-600">
                    {restroom.city}, {restroom.country}
                  </p>
                )}
              </div>

              {restroom.avg_overall > 0 && (
                <div className="flex items-center space-x-1 bg-psychedelic-purple text-white px-3 py-2 rounded-full">
                  <Star className="w-4 h-4 fill-current" />
                  <span className="font-semibold">{restroom.avg_overall.toFixed(1)}</span>
                  <span className="text-sm opacity-90">({restroom.review_count})</span>
                </div>
              )}
            </div>

            {restroom.description && (
              <p className="text-primary-700 mb-4">{restroom.description}</p>
            )}

            {/* Status indicators */}
            <div className="flex flex-wrap gap-2 mb-4">
              {restroom.is_verified && (
                <span className="bg-success/10 text-success px-3 py-1 rounded-full text-sm font-medium">
                  ✓ Verified
                </span>
              )}
              {restroom.temporarily_closed && (
                <span className="bg-warning/10 text-warning px-3 py-1 rounded-full text-sm font-medium">
                  ⚠️ Temporarily Closed
                </span>
              )}
              {restroom.permanently_closed && (
                <span className="bg-error/10 text-error px-3 py-1 rounded-full text-sm font-medium">
                  ❌ Permanently Closed
                </span>
              )}
              {!restroom.requires_fee && (
                <span className="bg-success/10 text-success px-3 py-1 rounded-full text-sm font-medium">
                  Free
                </span>
              )}
            </div>

            {/* Action buttons */}
            <div className="flex space-x-3">
              <button className="btn-primary flex items-center space-x-2 flex-1">
                <Navigation className="w-4 h-4" />
                <span>Get Directions</span>
              </button>
              <button className="btn-secondary flex items-center space-x-2">
                <Heart className="w-4 h-4" />
                <span>Save</span>
              </button>
              <button className="btn-secondary flex items-center space-x-2">
                <Share2 className="w-4 h-4" />
                <span>Share</span>
              </button>
            </div>
          </div>

          {/* Amenities & Features */}
          <div className="card">
            <h2 className="text-xl font-display font-semibold text-primary-800 mb-4">
              Amenities & Features
            </h2>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {/* Accessibility */}
              {restroom.wheelchair_accessible && restroom.wheelchair_accessible !== 'unknown' && (
                <div className="flex items-center space-x-3 p-3 bg-primary-50 rounded-lg">
                  <Accessibility className="w-6 h-6 text-psychedelic-purple" />
                  <div>
                    <div className="font-medium text-primary-800">Accessibility</div>
                    <div className="text-sm text-primary-600 capitalize">
                      {restroom.wheelchair_accessible}
                    </div>
                  </div>
                </div>
              )}

              {/* Baby changing */}
              {restroom.baby_changing && (
                <div className="flex items-center space-x-3 p-3 bg-primary-50 rounded-lg">
                  <Baby className="w-6 h-6 text-psychedelic-pink" />
                  <div>
                    <div className="font-medium text-primary-800">Baby Changing</div>
                    <div className="text-sm text-primary-600">Available</div>
                  </div>
                </div>
              )}

              {/* Gender neutral */}
              {restroom.gender_neutral && (
                <div className="flex items-center space-x-3 p-3 bg-primary-50 rounded-lg">
                  <Users className="w-6 h-6 text-psychedelic-orange" />
                  <div>
                    <div className="font-medium text-primary-800">Gender Neutral</div>
                    <div className="text-sm text-primary-600">Yes</div>
                  </div>
                </div>
              )}

              {/* Fee */}
              {restroom.requires_fee && (
                <div className="flex items-center space-x-3 p-3 bg-primary-50 rounded-lg">
                  <DollarSign className="w-6 h-6 text-psychedelic-yellow" />
                  <div>
                    <div className="font-medium text-primary-800">Fee Required</div>
                    <div className="text-sm text-primary-600">
                      {restroom.fee_amount ? `$${restroom.fee_amount}` : 'Yes'}
                    </div>
                  </div>
                </div>
              )}

              {/* Indoor/Outdoor */}
              <div className="flex items-center space-x-3 p-3 bg-primary-50 rounded-lg">
                <span className="text-2xl">{restroom.indoor ? '🏢' : '🌳'}</span>
                <div>
                  <div className="font-medium text-primary-800">Location</div>
                  <div className="text-sm text-primary-600">
                    {restroom.indoor ? 'Indoor' : 'Outdoor'}
                  </div>
                </div>
              </div>

              {/* Amenities */}
              {restroom.has_soap && (
                <div className="flex items-center space-x-3 p-3 bg-primary-50 rounded-lg">
                  <span className="text-2xl">🧼</span>
                  <div>
                    <div className="font-medium text-primary-800">Soap</div>
                    <div className="text-sm text-primary-600">Available</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Reviews Section */}
          {/* <ReviewSystem restroomId={restroom.id} /> */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-primary-800">Reviews</h3>
            <p className="text-primary-600">Review system temporarily disabled</p>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="card">
            <h3 className="text-lg font-display font-semibold text-primary-800 mb-4">
              Quick Stats
            </h3>

            <div className="space-y-3">
              {restroom.avg_cleanliness > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-primary-600">Cleanliness</span>
                  <div className="flex items-center space-x-1">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3 h-3 ${
                            i < Math.round(restroom.avg_cleanliness)
                              ? 'text-psychedelic-yellow fill-current'
                              : 'text-primary-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-sm font-medium text-primary-800">
                      {restroom.avg_cleanliness.toFixed(1)}
                    </span>
                  </div>
                </div>
              )}

              {restroom.avg_safety > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-primary-600">Safety</span>
                  <div className="flex items-center space-x-1">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3 h-3 ${
                            i < Math.round(restroom.avg_safety)
                              ? 'text-psychedelic-yellow fill-current'
                              : 'text-primary-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-sm font-medium text-primary-800">
                      {restroom.avg_safety.toFixed(1)}
                    </span>
                  </div>
                </div>
              )}

              {restroom.avg_accessibility > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-primary-600">Accessibility</span>
                  <div className="flex items-center space-x-1">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3 h-3 ${
                            i < Math.round(restroom.avg_accessibility)
                              ? 'text-psychedelic-yellow fill-current'
                              : 'text-primary-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-sm font-medium text-primary-800">
                      {restroom.avg_accessibility.toFixed(1)}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Info */}
          <div className="card">
            <h3 className="text-lg font-display font-semibold text-primary-800 mb-4">
              Information
            </h3>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-primary-600">Source</span>
                <span className="text-primary-800 capitalize">{restroom.source}</span>
              </div>

              <div className="flex justify-between">
                <span className="text-primary-600">Added</span>
                <span className="text-primary-800">
                  {format(new Date(restroom.created_at), 'MMM d, yyyy')}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-primary-600">Last Updated</span>
                <span className="text-primary-800">
                  {format(new Date(restroom.updated_at), 'MMM d, yyyy')}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-primary-600">Total Reviews</span>
                <span className="text-primary-800">{restroom.review_count}</span>
              </div>
            </div>
          </div>

          {/* Report Issues */}
          <div className="card">
            <h3 className="text-lg font-display font-semibold text-primary-800 mb-4">
              Report Issues
            </h3>
            <p className="text-sm text-primary-600 mb-4">
              Help keep information accurate by reporting any issues.
            </p>
            <button className="btn-secondary w-full text-sm">
              Report Problem
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RestroomDetailPage;
