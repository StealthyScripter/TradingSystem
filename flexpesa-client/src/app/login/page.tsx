import LoginForm from '@/components/auth/LoginForm';
import Link from 'next/link';

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900">
            Sign in to your account
          </h2>
        </div>

        <div className="bg-white py-8 px-4 shadow-lg rounded-lg">
          <LoginForm />

          <div className="mt-6 text-center">
            <Link
              href="/register"
              className="text-blue-600 hover:text-blue-500"
            >
              Don&#39;t have an account? Sign up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
