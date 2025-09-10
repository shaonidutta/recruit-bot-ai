// Test utility to verify authentication token handling
// This can be used in browser console to test login flow

export const testAuthFlow = async () => {
  console.log('🔍 Testing authentication flow...');
  
  // Clear any existing tokens
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  
  console.log('✅ Cleared existing tokens');
  
  // Test login with demo credentials
  try {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'password123'
      })
    });
    
    const data = await response.json();
    console.log('📡 Login response:', data);
    
    if (data.success && data.data) {
      const { user, tokens } = data.data;
      
      // Store tokens
      localStorage.setItem('accessToken', tokens.accessToken);
      localStorage.setItem('refreshToken', tokens.refreshToken);
      localStorage.setItem('user', JSON.stringify(user));
      
      console.log('✅ Tokens stored successfully:');
      console.log('- Access Token:', tokens.accessToken.substring(0, 20) + '...');
      console.log('- Refresh Token:', tokens.refreshToken.substring(0, 20) + '...');
      console.log('- User:', user);
      
      // Test authenticated API call
      const jobsResponse = await fetch('/api/v1/jobs', {
        headers: {
          'Authorization': `Bearer ${tokens.accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('📊 Jobs API response status:', jobsResponse.status);
      
      if (jobsResponse.status === 200) {
        console.log('✅ Authentication working! No 403 errors.');
      } else {
        console.log('❌ Still getting', jobsResponse.status, 'error');
      }
      
    } else {
      console.log('❌ Login failed:', data);
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
};

// Make it available globally for console testing
if (typeof window !== 'undefined') {
  window.testAuthFlow = testAuthFlow;
}