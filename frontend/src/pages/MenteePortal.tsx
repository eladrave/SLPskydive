import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AttendancePlanner from "@/components/mentee/AttendancePlanner";
import PreferenceEditor from "@/components/mentee/PreferenceEditor";
import ProgressionBoard from "@/components/mentee/ProgressionBoard";

const MenteePortal = () => {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Mentee Portal</h1>
      <p className="text-muted-foreground mb-8">
        Welcome! Manage your schedule, preferences, and track your progress.
      </p>

      <Tabs defaultValue="progression">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="progression">Progression Board</TabsTrigger>
          <TabsTrigger value="attendance">Attendance</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
          <TabsTrigger value="assignments">My Assignments</TabsTrigger>
        </TabsList>
        <TabsContent value="progression" className="mt-4">
          <ProgressionBoard />
        </TabsContent>
        <TabsContent value="attendance" className="mt-4">
          <AttendancePlanner />
        </TabsContent>
        <TabsContent value="preferences" className="mt-4">
          <PreferenceEditor />
        </TabsContent>
        <TabsContent value="assignments" className="mt-4">
            <h2 className="text-2xl font-semibold mb-4">Your Assignments</h2>
            <p className="text-sm text-muted-foreground">This feature is coming soon.</p>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MenteePortal;
