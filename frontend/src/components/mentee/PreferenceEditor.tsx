import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/contexts/AuthContext';

const PreferenceEditor = () => {
    const queryClient = useQueryClient();
    const { user } = useAuth();
    const [preferred, setPreferred] = useState('');
    const [avoided, setAvoided] = useState('');
    const [notes, setNotes] = useState('');

    const { data: preferences, isLoading } = useQuery({
        queryKey: ['preferences', user?.id],
        queryFn: () => apiClient.get('/preferences'),
        enabled: !!user,
    });

    // Populate form when data is fetched
    useEffect(() => {
        if (preferences) {
            setPreferred(preferences.preferred_mentors?.join(', ') || '');
            setAvoided(preferences.avoid_mentors?.join(', ') || '');
            setNotes(preferences.notes || '');
        }
    }, [preferences]);

    const updateMutation = useMutation({
        mutationFn: (updatedPreferences: any) => apiClient.put('/preferences', updatedPreferences),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['preferences', user?.id] });
            alert('Preferences updated successfully!');
        },
        onError: (error: any) => {
            alert(`Error: ${error.message}`);
        }
    });

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        const parseIds = (idString: string) => idString.split(',').map(s => s.trim()).filter(Boolean);

        updateMutation.mutate({
            preferred_mentors: parseIds(preferred),
            avoid_mentors: parseIds(avoided),
            notes: notes,
        });
    };

    if (isLoading) return <div>Loading preferences...</div>;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Mentor Preferences</CardTitle>
                <CardDescription>
                    Let us know who you'd prefer to work with. You can provide a comma-separated list of Mentor IDs.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="grid gap-4">
                    <div className="grid gap-2">
                        <Label htmlFor="preferred">Preferred Mentors (IDs)</Label>
                        <Input id="preferred" value={preferred} onChange={(e) => setPreferred(e.target.value)} />
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="avoided">Mentors to Avoid (IDs)</Label>
                        <Input id="avoided" value={avoided} onChange={(e) => setAvoided(e.target.value)} />
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="notes">Notes</Label>
                        <Textarea id="notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
                    </div>
                    <Button type="submit" disabled={updateMutation.isPending}>
                        {updateMutation.isPending ? 'Saving...' : 'Save Preferences'}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
};

export default PreferenceEditor;
