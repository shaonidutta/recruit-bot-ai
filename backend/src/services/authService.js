const User = require('../models/User');
const { generateTokens } = require('../utils/jwt');

/**
 * Authentication Service
 * Contains business logic for user authentication
 */

class AuthService {
  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} - User and tokens
   */
  async registerUser(userData) {
    const { name, email, password } = userData;

    // Check if user already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      throw new Error('User with this email already exists');
    }

    // Create new user
    const user = new User({
      name,
      email,
      password // Will be hashed by the pre-save middleware
    });

    await user.save();

    // Generate tokens
    const tokens = generateTokens(user);

    // Return user data without password
    const userData_response = {
      id: user._id,
      name: user.name,
      email: user.email,
      createdAt: user.createdAt
    };

    return {
      user: userData_response,
      ...tokens
    };
  }

  /**
   * Login user
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} - User and tokens
   */
  async loginUser(email, password) {
    // Find user by email (include password for comparison)
    const user = await User.findByEmailWithPassword(email);
    if (!user) {
      throw new Error('Invalid email or password');
    }

    // Check password
    const isPasswordValid = await user.comparePassword(password);
    if (!isPasswordValid) {
      throw new Error('Invalid email or password');
    }

    // Generate tokens
    const tokens = generateTokens(user);

    // Return user data without password
    const userData = {
      id: user._id,
      name: user.name,
      email: user.email,
      createdAt: user.createdAt
    };

    return {
      user: userData,
      ...tokens
    };
  }

  /**
   * Get user profile by ID
   * @param {string} userId - User ID
   * @returns {Promise<Object>} - User data
   */
  async getUserProfile(userId) {
    const user = await User.findById(userId);
    if (!user) {
      throw new Error('User not found');
    }

    return {
      id: user._id,
      name: user.name,
      email: user.email,
      createdAt: user.createdAt,
      updatedAt: user.updatedAt
    };
  }



  /**
   * Refresh user tokens
   * @param {string} userId - User ID
   * @returns {Promise<Object>} - New tokens
   */
  async refreshUserTokens(userId) {
    const user = await User.findById(userId);
    if (!user) {
      throw new Error('User not found');
    }

    // Generate new tokens
    return generateTokens(user);
  }
}

module.exports = new AuthService();
