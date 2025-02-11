import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import GitHubProvider from "next-auth/providers/github";
import CredentialsProvider from "next-auth/providers/credentials";

interface OAuthUser {
  email?: string;
  name?: string;
  image?: string;
  id?: string;
}

function isExtendedUser(user: unknown): user is { id: string } {
  return (
    typeof user === "object" &&
    user !== null &&
    "id" in user &&
    typeof (user as { id: unknown }).id === "string"
  );
}

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "text", placeholder: "jsmith@example.com" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const res = await fetch(
          process.env.NEXT_PUBLIC_BACKEND_URL! + "/api/auth/signin",
          {
            method: "POST",
            body: JSON.stringify({
              email: credentials?.email,
              password: credentials?.password,
            }),
            headers: { "Content-Type": "application/json" },
          }
        );
        const rawText = await res.text();
        try {
          const user = JSON.parse(rawText);
          if (res.ok && user) {
            return user;
          }
        } catch (error) {
          console.error("JSON parse error in authorize:", error, rawText);
        }
        throw new Error("Invalid credentials");
      },
    }),
  ],
  pages: {
    signIn: "/signin", // Custom sign in page
    error: "/error",   // Custom error page (if needed)
    newUser: "/signup", // Custom signup page
  },
  callbacks: {
    async redirect({ url, baseUrl }): Promise<string> {
      if (url.startsWith("/")) return `${baseUrl}${url}`;
      if (url.startsWith(baseUrl)) return url;
      return baseUrl;
    },
    async jwt({ token, user }) {
      if (user) {
        if (isExtendedUser(user)) {
          token.id = user.id;
        } else {
          const oauthUser = user as OAuthUser;
          if (oauthUser.email) {
            try {
              const res = await fetch(
                process.env.NEXT_PUBLIC_BACKEND_URL! + "/api/auth/oauth-signin",
                {
                  method: "POST",
                  body: JSON.stringify({
                    email: oauthUser.email,
                    name: oauthUser.name,
                    image: oauthUser.image,
                  }),
                  headers: { "Content-Type": "application/json" },
                }
              );
              const dbUser = await res.json();
              token.id = dbUser.id;
            } catch (err) {
              console.error("Error upserting OAuth user:", err);
            }
          }
        }
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
      }
      return session;
    },
  },
  session: {
    strategy: "jwt",
  },
  debug: true,
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
export {};
