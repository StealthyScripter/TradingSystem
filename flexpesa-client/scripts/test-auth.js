import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

class FrontendAuthTester {
  constructor() {
    this.testUser = {
      email: 'frontend-test@example.com',
      password: 'testpassword123',
      first_name: 'Frontend',
      last_name: 'Test'
    };
    this.cookies = '';
  }

  log(message, type = 'info') {
    const colors = {
      info: '\x1b[36m',    // cyan
      success: '\x1b[32m', // green
      error: '\x1b[31m',   // red
      warning: '\x1b[33m'  // yellow
    };
    const reset = '\x1b[0m';
    console.log(`${colors[type]}[${type.toUpperCase()}]${reset} ${message}`);
  }

  async testBackendConnection() {
    this.log('🔗 Testing backend connection...', 'info');

    try {
      await axios.get(`${API_BASE}/../`);
      this.log('✅ Backend is running', 'success');
      return true;
    } catch (error) {
      this.log('❌ Backend not accessible. Start with: python run.py', 'error');
      return false;
    }
  }

  async testLogin() {
    this.log('🧪 Testing login...', 'info');

    try {
      const formData = new URLSearchParams();
      formData.append('username', 'admin@portfolio.com');
      formData.append('password', 'password');

      const response = await axios.post(`${API_BASE}/auth/cookie/login`, formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        withCredentials: true
      });

      // Extract cookies
      const setCookieHeader = response.headers['set-cookie'];
      if (setCookieHeader) {
        this.cookies = setCookieHeader.join('; ');
      }

      this.log('✅ Login successful', 'success');
      return true;
    } catch (error) {
      this.log(`❌ Login failed: ${error.response?.data?.detail || error.message}`, 'error');
      return false;
    }
  }

  async testProtectedRoute() {
    this.log('🧪 Testing protected route...', 'info');

    try {
      const response = await axios.get(`${API_BASE}/portfolio/summary`, {
        headers: { 'Cookie': this.cookies },
        withCredentials: true
      });

      this.log('✅ Protected route accessible', 'success');
      this.log(`📊 Portfolio: ${response.data.accounts?.length || 0} accounts, $${response.data.total_value?.toFixed(2) || 0}`, 'info');
      return true;
    } catch (error) {
      this.log(`❌ Protected route failed: ${error.response?.status}`, 'error');
      return false;
    }
  }

  async runTests() {
    this.log('🚀 Starting Frontend Auth Tests', 'info');

    const tests = [
      () => this.testBackendConnection(),
      () => this.testLogin(),
      () => this.testProtectedRoute()
    ];

    let passed = 0;
    for (const test of tests) {
      if (await test()) passed++;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    this.log(`🎯 Results: ${passed}/${tests.length} tests passed`, passed === tests.length ? 'success' : 'warning');
    return passed === tests.length;
  }
}

if (require.main === module) {
  const tester = new FrontendAuthTester();
  tester.runTests().then(success => process.exit(success ? 0 : 1));
}