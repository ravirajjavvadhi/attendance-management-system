import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

export default withAuth(
  function middleware(req) {
    const token = req.nextauth.token;
    const path = req.nextUrl.pathname;
    const role = (token?.role as string) || "";

    // Define allowed paths per role
    const roleRoutes: Record<string, string[]> = {
      SUPERADMIN: ["/dashboard/superadmin", "/dashboard/admin/reports"],
      MANAGEMENT: ["/dashboard/principal", "/dashboard/admin/staff", "/dashboard/student", "/dashboard/admin/reports", "/setup"],
      FACULTY: ["/dashboard/faculty", "/dashboard/student"],
      STUDENT: ["/dashboard/student"],
    };

    const defaultRedirects: Record<string, string> = {
      SUPERADMIN: "/dashboard/superadmin",
      MANAGEMENT: "/dashboard/principal",
      FACULTY: "/dashboard/faculty",
      STUDENT: "/dashboard/student",
    };

    // Check if user is trying to access a page they don't have permission for
    let allowed = false;

    // Helper to check if a route is allowed
    const isRouteAllowed = (targetPath: string, userRole: string) => {
      const allowedRoutes = roleRoutes[userRole] || [];
      return allowedRoutes.some((route) => targetPath.startsWith(route));
    };

    if (path.startsWith("/dashboard") || path === "/setup") {
      if (!role) {
        const errorMsg = token?.error ? `?error=${encodeURIComponent(token.error as string)}` : "";
        return NextResponse.redirect(new URL(`/login${errorMsg}`, req.url));
      }
      
      allowed = isRouteAllowed(path, role);
      
      if (!allowed) {
        // Redirect to their default dashboard home if they try to access something else
        const destination = defaultRedirects[role] || "/login";
        return NextResponse.redirect(new URL(destination, req.url));
      }
    }

    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
);

export const config = {
  matcher: ["/dashboard/:path*", "/setup"],
};
