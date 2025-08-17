import React from 'react';

import {
  Award,
  Calendar,
  MapPin,
  Star,
} from 'lucide-react';

import { useAuthStore } from '../lib/store';

const ProfilePage: React.FC = () => {
  const user = useAuthStore((state) => state.user);

  if (!user) return null;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Info */}
        <div className="lg:col-span-1">
          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <PuperLogo size="xl" showText={false} />
            </div>
            <h2 className="text-xl font-display font-bold text-primary-800 mb-1">
              {user.full_name || user.username}
            </h2>
            <p className="text-primary-600 mb-4">@{user.username}</p>
            
            <div className="bg-psychedelic-2 text-white rounded-lg p-4 mb-4">
              <div className="text-2xl font-bold">{user.points}</div>
              <div className="text-sm opacity-90">Total Points</div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-primary-600">Member since</span>
                <span className="text-primary-800">
                  {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-primary-600">Role</span>
                <span className="text-primary-800 capitalize">{user.role}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Stats and Badges */}
        <div className="lg:col-span-2 space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card-hover text-center">
              <MapPin className="w-8 h-8 text-psychedelic-purple mx-auto mb-2" />
              <div className="text-2xl font-bold text-primary-800">0</div>
              <div className="text-sm text-primary-600">Restrooms Added</div>
            </div>
            
            <div className="card-hover text-center">
              <Star className="w-8 h-8 text-psychedelic-pink mx-auto mb-2" />
              <div className="text-2xl font-bold text-primary-800">0</div>
              <div className="text-sm text-primary-600">Reviews Written</div>
            </div>
            
            <div className="card-hover text-center">
              <Award className="w-8 h-8 text-psychedelic-orange mx-auto mb-2" />
              <div className="text-2xl font-bold text-primary-800">{user.badges.length}</div>
              <div className="text-sm text-primary-600">Badges Earned</div>
            </div>
            
            <div className="card-hover text-center">
              <Calendar className="w-8 h-8 text-psychedelic-cyan mx-auto mb-2" />
              <div className="text-2xl font-bold text-primary-800">0</div>
              <div className="text-sm text-primary-600">Days Active</div>
            </div>
          </div>

          {/* Badges */}
          <div className="card">
            <h3 className="text-lg font-display font-semibold text-primary-800 mb-4">
              Badges & Achievements
            </h3>
            
            {user.badges.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {user.badges.map((badge, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-primary-50 rounded-lg">
                    <div className="w-10 h-10 bg-psychedelic-1 rounded-lg flex items-center justify-center">
                      <span className="text-white text-lg">🏆</span>
                    </div>
                    <div>
                      <div className="font-medium text-primary-800 capitalize">
                        {badge.replace('_', ' ')}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Award className="w-8 h-8 text-primary-400" />
                </div>
                <h4 className="text-lg font-semibold text-primary-700 mb-2">
                  No badges yet
                </h4>
                <p className="text-primary-600 text-sm">
                  Start contributing to earn your first badge!
                </p>
              </div>
            )}
          </div>

          {/* Recent Activity */}
          <div className="card">
            <h3 className="text-lg font-display font-semibold text-primary-800 mb-4">
              Recent Activity
            </h3>
            
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Calendar className="w-8 h-8 text-primary-400" />
              </div>
              <h4 className="text-lg font-semibold text-primary-700 mb-2">
                No activity yet
              </h4>
              <p className="text-primary-600 text-sm">
                Your recent reviews and contributions will appear here.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
