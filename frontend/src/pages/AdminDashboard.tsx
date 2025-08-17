import RosterView from "@/components/admin/RosterView";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const AdminDashboard = () => {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Admin Dashboard</h1>
      <p className="text-muted-foreground mb-8">
        Welcome, admin! Here you can manage the entire system.
      </p>

      <div className="grid gap-8">
        <RosterView />

        <Card>
            <CardHeader>
                <CardTitle>Matching Service</CardTitle>
            </CardHeader>
            <CardContent>
                <p className="text-sm text-muted-foreground">
                    The matching runner and preview tools are coming soon.
                </p>
            </CardContent>
        </Card>

        <Card>
            <CardHeader>
                <CardTitle>Capacity Heatmap</CardTitle>
            </CardHeader>
            <CardContent>
                <p className="text-sm text-muted-foreground">
                    The capacity heatmap feature is coming soon.
                </p>
            </CardContent>
        </Card>

      </div>
    </div>
  );
};

export default AdminDashboard;
