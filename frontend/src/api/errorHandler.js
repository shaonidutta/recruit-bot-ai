export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return new Error(data.message || 'Bad request');
      case 401:
        return new Error(data.message || 'Invalid credentials');
      case 403:
        return new Error('Forbidden - insufficient permissions');
      case 404:
        return new Error('Resource not found');
      case 409:
        return new Error(data.message || 'Conflict - resource already exists');
      case 422:
        return new Error(data.message || 'Validation error');
      case 500:
        return new Error('Server error - please try again later');
      default:
        return new Error(data.message || 'An error occurred');
    }
  } else if (error.request) {
    // Network error
    return new Error('Network error - check your connection');
  } else {
    // Other error
    return new Error('An unexpected error occurred');
  }
};
