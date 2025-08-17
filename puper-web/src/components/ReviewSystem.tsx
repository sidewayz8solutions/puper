import React, { useState } from 'react';
import { Star, ThumbsUp, Camera, Send } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reviewAPI, Review } from '../lib/api';
import { useAuthStore } from '../lib/store';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

const reviewSchema = z.object({
  cleanliness: z.number().min(1).max(5),
  lighting: z.number().min(1).max(5),
  safety: z.number().min(1).max(5),
  privacy: z.number().min(1).max(5),
  accessibility: z.number().min(1).max(5),
  overall: z.number().min(1).max(5),
  comment: z.string().max(1000).optional(),
});

type ReviewForm = z.infer<typeof reviewSchema>;

interface ReviewSystemProps {
  restroomId: string;
  className?: string;
}

const ReviewSystem: React.FC<ReviewSystemProps> = ({ restroomId, className = '' }) => {
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [ratings, setRatings] = useState({
    cleanliness: 0,
    lighting: 0,
    safety: 0,
    privacy: 0,
    accessibility: 0,
    overall: 0,
  });

  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ReviewForm>({
    resolver: zodResolver(reviewSchema),
  });

  // Fetch reviews
  const { data: reviews, isLoading } = useQuery({
    queryKey: ['reviews', restroomId],
    queryFn: async () => {
      const response = await reviewAPI.getByRestroom(restroomId);
      return response.data;
    },
  });

  // Submit review mutation
  const submitReviewMutation = useMutation({
    mutationFn: async (data: ReviewForm) => {
      const response = await reviewAPI.create({
        restroom_id: restroomId,
        ...data,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', restroomId] });
      queryClient.invalidateQueries({ queryKey: ['restrooms'] });
      toast.success('Review submitted successfully!');
      setShowReviewForm(false);
      reset();
      setRatings({
        cleanliness: 0,
        lighting: 0,
        safety: 0,
        privacy: 0,
        accessibility: 0,
        overall: 0,
      });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to submit review');
    },
  });

  // Mark review helpful mutation
  const markHelpfulMutation = useMutation({
    mutationFn: async (reviewId: string) => {
      const response = await reviewAPI.markHelpful(reviewId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', restroomId] });
      toast.success('Thank you for your feedback!');
    },
  });

  const onSubmit = (data: ReviewForm) => {
    submitReviewMutation.mutate(data);
  };

  const StarRating: React.FC<{
    value: number;
    onChange: (value: number) => void;
    label: string;
    name: keyof ReviewForm;
  }> = ({ value, onChange, label, name }) => (
    <div className="flex items-center justify-between">
      <label className="text-sm font-medium text-primary-700">{label}</label>
      <div className="flex space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => {
              onChange(star);
              setRatings(prev => ({ ...prev, [name]: star }));
            }}
            className="focus:outline-none"
          >
            <Star
              className={`w-5 h-5 ${
                star <= value
                  ? 'text-psychedelic-yellow fill-current'
                  : 'text-primary-300'
              }`}
            />
          </button>
        ))}
      </div>
    </div>
  );

  const ReviewCard: React.FC<{ review: Review }> = ({ review }) => (
    <div className="card p-4">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-semibold text-primary-800">
            {review.username || 'Anonymous'}
          </h4>
          <p className="text-xs text-primary-600">
            {format(new Date(review.created_at), 'MMM d, yyyy')}
          </p>
        </div>
        <div className="flex items-center space-x-1 bg-psychedelic-purple text-white px-2 py-1 rounded-full text-sm">
          <Star className="w-3 h-3 fill-current" />
          <span>{review.overall}</span>
        </div>
      </div>

      {/* Rating breakdown */}
      <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
        <div className="flex justify-between">
          <span className="text-primary-600">Cleanliness:</span>
          <div className="flex">
            {[...Array(review.cleanliness)].map((_, i) => (
              <Star key={i} className="w-3 h-3 text-psychedelic-yellow fill-current" />
            ))}
          </div>
        </div>
        <div className="flex justify-between">
          <span className="text-primary-600">Safety:</span>
          <div className="flex">
            {[...Array(review.safety)].map((_, i) => (
              <Star key={i} className="w-3 h-3 text-psychedelic-yellow fill-current" />
            ))}
          </div>
        </div>
        <div className="flex justify-between">
          <span className="text-primary-600">Lighting:</span>
          <div className="flex">
            {[...Array(review.lighting)].map((_, i) => (
              <Star key={i} className="w-3 h-3 text-psychedelic-yellow fill-current" />
            ))}
          </div>
        </div>
        <div className="flex justify-between">
          <span className="text-primary-600">Privacy:</span>
          <div className="flex">
            {[...Array(review.privacy)].map((_, i) => (
              <Star key={i} className="w-3 h-3 text-psychedelic-yellow fill-current" />
            ))}
          </div>
        </div>
      </div>

      {review.comment && (
        <p className="text-sm text-primary-700 mb-3">{review.comment}</p>
      )}

      <div className="flex items-center justify-between">
        <button
          onClick={() => markHelpfulMutation.mutate(review.id)}
          className="flex items-center space-x-1 text-xs text-primary-600 hover:text-psychedelic-purple transition-colors"
          disabled={markHelpfulMutation.isPending}
        >
          <ThumbsUp className="w-3 h-3" />
          <span>Helpful ({review.helpful_count})</span>
        </button>
        
        {review.is_verified && (
          <span className="text-xs text-success font-medium">✓ Verified</span>
        )}
      </div>
    </div>
  );

  return (
    <div className={className}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-display font-bold text-primary-800">
          Reviews & Ratings
        </h2>
        {user && !showReviewForm && (
          <button
            onClick={() => setShowReviewForm(true)}
            className="btn-psychedelic text-sm py-2 px-4"
          >
            Write Review
          </button>
        )}
      </div>

      {/* Review Form */}
      {showReviewForm && (
        <div className="card p-6 mb-6">
          <h3 className="text-lg font-semibold text-primary-800 mb-4">
            Share Your Experience
          </h3>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Rating inputs */}
            <div className="space-y-3">
              <StarRating
                value={ratings.overall}
                onChange={(value) => register('overall', { value })}
                label="Overall Rating"
                name="overall"
              />
              <StarRating
                value={ratings.cleanliness}
                onChange={(value) => register('cleanliness', { value })}
                label="Cleanliness"
                name="cleanliness"
              />
              <StarRating
                value={ratings.lighting}
                onChange={(value) => register('lighting', { value })}
                label="Lighting"
                name="lighting"
              />
              <StarRating
                value={ratings.safety}
                onChange={(value) => register('safety', { value })}
                label="Safety"
                name="safety"
              />
              <StarRating
                value={ratings.privacy}
                onChange={(value) => register('privacy', { value })}
                label="Privacy"
                name="privacy"
              />
              <StarRating
                value={ratings.accessibility}
                onChange={(value) => register('accessibility', { value })}
                label="Accessibility"
                name="accessibility"
              />
            </div>

            {/* Comment */}
            <div>
              <label className="block text-sm font-medium text-primary-700 mb-2">
                Comment (optional)
              </label>
              <textarea
                {...register('comment')}
                rows={3}
                className="input-primary"
                placeholder="Share details about your experience..."
              />
              {errors.comment && (
                <p className="mt-1 text-sm text-error">{errors.comment.message}</p>
              )}
            </div>

            {/* Actions */}
            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={submitReviewMutation.isPending}
                className="btn-psychedelic flex items-center space-x-2 disabled:opacity-50"
              >
                {submitReviewMutation.isPending ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                <span>Submit Review</span>
              </button>
              
              <button
                type="button"
                onClick={() => setShowReviewForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Reviews List */}
      {isLoading ? (
        <div className="text-center py-8">
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-primary-600">Loading reviews...</p>
        </div>
      ) : reviews && reviews.length > 0 ? (
        <div className="space-y-4">
          {reviews.map((review) => (
            <ReviewCard key={review.id} review={review} />
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <Star className="w-12 h-12 text-primary-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-primary-700 mb-2">
            No reviews yet
          </h3>
          <p className="text-primary-600 text-sm">
            Be the first to share your experience!
          </p>
        </div>
      )}
    </div>
  );
};

export default ReviewSystem;
