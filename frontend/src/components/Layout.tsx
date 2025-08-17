import { Link, Outlet } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const Layout = () => {
  const { user, logout, isLoading } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-primary text-primary-foreground shadow">
        <nav className="container mx-auto px-6 py-3 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold hover:text-primary-foreground/90">
            Skydiving Scheduler
          </Link>
          <div className="flex items-center gap-4">
            {isLoading ? (
                <div>Loading...</div>
            ) : user ? (
              <>
                <span className="font-semibold">Welcome, {user.name}</span>
                {user.role === 'mentor' && <Link to="/mentor" className="hover:underline">Mentor Portal</Link>}
                {user.role === 'mentee' && <Link to="/mentee" className="hover:underline">Mentee Portal</Link>}
                {user.role === 'admin' && <Link to="/admin" className="hover:underline">Admin</Link>}
                <button onClick={() => logout()} className="font-semibold hover:underline">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="font-semibold hover:underline">Login</Link>
                <Link to="/signup" className="font-semibold hover:underline">Signup</Link>
              </>
            )}
          </div>
        </nav>
      </header>
      <main className="flex-grow container mx-auto p-6">
        <Outlet />
      </main>
      <footer className="bg-secondary text-secondary-foreground py-4">
        <div className="container mx-auto text-center text-sm">
            © 2024 Skydiving Training Center. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default Layout;
