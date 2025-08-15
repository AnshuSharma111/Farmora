const mongoose = require('mongoose');

const querySchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    appwriteId: {
      type: String,
      required: true,
      index: true,
    },
    question: {
      type: String,
      required: true,
      trim: true,
    },
    intent: {
      type: String,
      enum: ['weather', 'soil_health', 'crop_choice', 'pest_control', 'market_prices', 'general'],
      default: 'general',
    },
    location: {
      type: String,
      trim: true,
    },
    language: {
      type: String,
      default: 'en',
    },
    answer: {
      type: String,
      trim: true,
    },
    sources: [{
      type: String,
      trim: true,
    }],
    confidence: {
      type: Number,
      min: 0,
      max: 1,
      default: 0,
    },
    feedback: {
      helpful: {
        type: Boolean,
        default: null,
      },
      comments: {
        type: String,
        trim: true,
      },
    },
    metadata: {
      weatherConditions: {
        type: Map,
        of: String,
      },
      soilData: {
        type: Map,
        of: String,
      },
      cropData: {
        type: Map,
        of: String,
      },
      additionalContext: {
        type: Map,
        of: String,
      },
    },
  },
  {
    timestamps: true,
  }
);

// Add text index for search functionality
querySchema.index({ question: 'text', answer: 'text' });

const Query = mongoose.model('Query', querySchema);

module.exports = Query;
