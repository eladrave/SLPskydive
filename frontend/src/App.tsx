import { Routes, Route } from "react-router-dom";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";

// Pages
import HomePage from "@/pages/HomePage";
import LoginPage from "@/pages/LoginPage";
import SignupPage from "@/pages/SignupPage";
import MentorPortal from "@/pages/MentorPortal";
import MenteePortal from "@/pages/MenteePortal";
import AdminDashboard from "@/pages/AdminDashboard";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        {/* Public routes */}
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="signup" element={<SignupPage />} />

        {/* Protected routes */}
        <Route element={<ProtectedRoute allowedRoles={['mentor']} />}>
          <Route path="mentor" element={<MentorPortal />} />
        </Route>
        <Route element={<ProtectedRoute allowedRoles={['mentee']} />}>
          <Route path="mentee" element={<MenteePortal />} />
        </Route>
        <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
          <Route path="admin" element={<AdminDashboard />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
