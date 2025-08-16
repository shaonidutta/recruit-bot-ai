import React from 'react';
import { useAuth } from '../../context/AuthContext.jsx';
import { Button } from '../../components/ui/Button.jsx';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card.jsx';

const DashboardPage = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                AI Recruitment Agent
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user?.name}
              </span>
              <Button variant="outline" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">
            Real-Time Command Center
          </h2>
          <p className="text-gray-600">
            Dashboard coming soon - Authentication is working! 🎉
          </p>
        </div>

        {/* Success Message */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-green-600">
              ✅ Authentication System Complete!
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                <strong>User:</strong> {user?.name} ({user?.email})
              </p>
              <p className="text-sm text-gray-600">
                <strong>Role:</strong> {user?.role}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Status:</strong> Successfully authenticated with JWT token
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Next Steps */}
        <Card>
          <CardHeader>
            <CardTitle>Next Steps</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>✅ Authentication system implemented</li>
              <li>✅ Context API for state management</li>
              <li>✅ Shadcn UI components integrated</li>
              <li>✅ Form validation and error handling</li>
              <li>✅ Protected routes working</li>
              <li>🔄 Next: Build dashboard components</li>
              <li>🔄 Next: Integrate with backend APIs</li>
            </ul>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default DashboardPage;
