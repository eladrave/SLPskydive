import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea'; // I'll need this, let's add it

const SignoffForm = () => {
    const queryClient = useQueryClient();
    const [selectedMentee, setSelectedMentee] = useState<string>('');
    const [selectedStep, setSelectedStep] = useState<string>('');
    const [notes, setNotes] = useState('');
    const [evidenceUrl, setEvidenceUrl] = useState('');

    // Fetch mentees
    const { data: mentees, isLoading: isLoadingMentees } = useQuery<any[]>({
        queryKey: ['users', 'mentee'],
        queryFn: () => apiClient.get('/users?role=mentee'),
    });

    // Fetch progression steps
    const { data: steps, isLoading: isLoadingSteps } = useQuery<any[]>({
        queryKey: ['progressionSteps'],
        queryFn: () => apiClient.get('/progression/steps'),
    });

    // Mutation for completing a step
    const completeStepMutation = useMutation({
        mutationFn: (completionData: any) =>
            apiClient.post(`/progression/${completionData.step_id}/complete`, completionData.body),
        onSuccess: () => {
            // Optionally invalidate queries to refetch data
            alert('Step signed off successfully!');
            // Reset form
            setSelectedMentee('');
            setSelectedStep('');
            setNotes('');
            setEvidenceUrl('');
        },
        onError: (error: any) => {
            alert(`Error: ${error.message}`);
        }
    });

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        if (!selectedMentee || !selectedStep) {
            alert('Please select a mentee and a progression step.');
            return;
        }
        completeStepMutation.mutate({
            step_id: selectedStep,
            body: {
                mentee_id: selectedMentee,
                notes,
                evidence_url: evidenceUrl,
            }
        });
    };

    if (isLoadingMentees || isLoadingSteps) return <div>Loading form data...</div>;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Sign Off Progression Step</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="grid gap-6">
                    <div className="grid gap-2">
                        <Label htmlFor="mentee">Mentee</Label>
                        <Select onValueChange={setSelectedMentee} value={selectedMentee}>
                            <SelectTrigger id="mentee">
                                <SelectValue placeholder="Select a mentee" />
                            </SelectTrigger>
                            <SelectContent>
                                {mentees?.map(mentee => (
                                    <SelectItem key={mentee.id} value={mentee.id}>{mentee.name}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="step">Progression Step</Label>
                        <Select onValueChange={setSelectedStep} value={selectedStep}>
                            <SelectTrigger id="step">
                                <SelectValue placeholder="Select a step" />
                            </SelectTrigger>
                            <SelectContent>
                                {steps?.map(step => (
                                    <SelectItem key={step.id} value={step.id}>{step.title} ({step.category})</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="notes">Notes</Label>
                        <Textarea id="notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="evidenceUrl">Evidence URL (Optional)</Label>
                        <Input id="evidenceUrl" value={evidenceUrl} onChange={(e) => setEvidenceUrl(e.target.value)} />
                    </div>
                    <Button type="submit" disabled={completeStepMutation.isPending}>
                        {completeStepMutation.isPending ? 'Submitting...' : 'Sign Off Step'}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
};

export default SignoffForm;
