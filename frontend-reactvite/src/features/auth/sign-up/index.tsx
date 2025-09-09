import { useSearch } from "@tanstack/react-router";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { AuthLayout } from "../auth-layout";
import { UserSignUpForm } from "./components/user-signup-form";

export function SignUp() {
  const { redirect } = useSearch({ from: "/(auth)/sign-up" });

  return (
    <AuthLayout>
      <Card className="gap-4">
        <CardHeader>
          <CardTitle className="text-lg tracking-tight">Create Account</CardTitle>
          <CardDescription>
            Sign up for a new account to get started <br />
            with our platform
          </CardDescription>
        </CardHeader>
        <CardContent>
          <UserSignUpForm redirectTo={redirect} />
        </CardContent>
        <CardFooter>
          <p className="text-muted-foreground px-8 text-center text-sm">
            Already have an account?{" "}
            <a
              href="/sign-in"
              className="hover:text-primary underline underline-offset-4"
            >
              Sign in
            </a>
            .
          </p>
        </CardFooter>
      </Card>
    </AuthLayout>
  );
}
