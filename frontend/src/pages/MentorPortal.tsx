import AvailabilityEditor from '@/components/mentor/AvailabilityEditor';
import SignoffForm from '@/components/mentor/SignoffForm';

const MentorPortal = () => {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Mentor Portal</h1>
      <p className="text-muted-foreground">
        Welcome, mentor! Here you can manage your availability, assignments, and signoffs.
      </p>

      <div className="mt-8 grid md:grid-cols-2 gap-8">
          <div className="md:col-span-2 lg:col-span-1">
              <AvailabilityEditor />
          </div>
          <div className="md:col-span-2 lg:col-span-1">
            <div className="grid gap-8">
                <div>
                    <h2 className="text-2xl font-semibold mb-4">Sign-off a Jump</h2>
                    <SignoffForm />
                </div>
                <div>
                    <h2 className="text-2xl font-semibold mb-4">Pending Assignments</h2>
                    <p className="text-sm text-muted-foreground">This feature is coming soon.</p>
                </div>
            </div>
          </div>
      </div>
    </div>
  );
};

export default MentorPortal;
