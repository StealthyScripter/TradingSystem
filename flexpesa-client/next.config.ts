import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    // Enable if needed
  },
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
    ]
  },
};

export default nextConfig;
