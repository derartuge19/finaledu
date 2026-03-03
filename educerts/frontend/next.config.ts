import type { NextConfig } from "next";
// @ts-expect-error - next-pwa has no types
import withPWAInit from "next-pwa";

const withPWA = withPWAInit({
  dest: "public",
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === "development",
  buildExcludes: [/middleware-manifest\.json$/],
});

const nextConfig: NextConfig = {
  turbopack: {},
};

export default withPWA(nextConfig);
