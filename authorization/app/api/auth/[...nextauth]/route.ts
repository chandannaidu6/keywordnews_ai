import NextAuth, { NextAuthOptions } from "next-auth";
import { JWT } from "next-auth/jwt";
import GoogleProvider from "next-auth/providers/google";
import GitHubProvider from "next-auth/providers/github";
import CredentialsProvider from "next-auth/providers/credentials";

export interface MyUser {
  id: string;    
  email: string;
  name: string;
  image: string;
}

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      profile(profile, _unusedTokens: unknown): MyUser {
        void _unusedTokens;
        return {
          id: String(profile.sub),
          email: String(profile.email),
          name: String(profile.name),
          image: String(profile.picture),
        };
      },
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      profile(profile, _unusedTokens: unknown): MyUser {
        void _unusedTokens;
        return {
          id: String(profile.id),
          email: String(profile.email),
          name: String(profile.name),
          image: String(profile.avatar_url),
        };
      },
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
        if (!res.ok) {
          throw new Error(await res.text());
        }
        const user = await res.json();
        return user as MyUser;
      },
    }),
  ],
  pages: {
    signIn: "/signin",  
    error: "/error",    
    newUser: "/signup", 
  },
  callbacks: {
    async redirect({ url, baseUrl }): Promise<string> {
      if (url.startsWith("/")) return `${baseUrl}${url}`;
      if (url.startsWith(baseUrl)) return url;
      return baseUrl;
    },
    async jwt({ token, user, account }): Promise<JWT> {
      if (user) {
        if (account && (account.provider === "google" || account.provider === "github")) {
          try {
            const res = await fetch(
              process.env.NEXT_PUBLIC_BACKEND_URL! + "/api/auth/oauth-signin",
              {
                method: "POST",
                body: JSON.stringify({
                  email: user.email,
                  name: user.name,
                  image: user.image,
                }),
                headers: { "Content-Type": "application/json" },
              }
            );
            if (!res.ok) {
              const errorText = await res.text();
              console.error("OAuth upsert endpoint error:", errorText);
              throw new Error("OAuth upsert failed");
            }
            const dbUser = await res.json();
            token.id = dbUser.id;
          } catch (err) {
            console.error("Error upserting OAuth user:", err);
          }
        } else {
          token.id = user.id;
        }
      }
      return token;
    },
    async session({ session, token }): Promise<typeof session> {
      if (session.user) {
        session.user.id = token.id as string;
      }
      return session;
    },
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  debug: process.env.NODE_ENV === "development",
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
export {};
