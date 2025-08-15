const mongoose = require('mongoose');

const userSchema = new mongoose.Schema(
  {
    appwriteId: {
      type: String,
      required: [true, 'Appwrite ID is required'],
      unique: true,
      index: true,
    },
    name: {
      type: String,
      required: [true, 'Name is required'],
      trim: true,
    },
    email: {
      type: String,
      required: [true, 'Email is required'],
      unique: true,
      lowercase: true,
      trim: true,
      validate: {
        validator: function(v) {
          return /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(v);
        },
        message: 'Please enter a valid email address',
      },
    },
    role: {
      type: String,
      enum: ['user', 'admin'],
      default: 'user',
    },
    location: {
      type: String,
      trim: true,
      default: '',
    },
    preferredLanguage: {
      type: String,
      default: 'en',
    },
    farmDetails: {
      farmSize: {
        type: Number,
        default: 0,
      },
      cropTypes: [{
        type: String,
        trim: true,
      }],
      soilType: {
        type: String,
        trim: true,
        default: '',
      },
    },
    previousQueries: [{
      question: String,
      answer: String,
      timestamp: {
        type: Date,
        default: Date.now,
      },
    }],
    isActive: {
      type: Boolean,
      default: true,
    },
  },
  {
    timestamps: true,
  }
);

// No password-related methods are needed as authentication is handled by Appwrite

const User = mongoose.model('User', userSchema);

module.exports = User;
