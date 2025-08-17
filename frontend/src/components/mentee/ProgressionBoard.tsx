import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { CheckCircle2, Circle, Award } from 'lucide-react';

const ProgressionBoard = () => {
    const { user } = useAuth();

    const { data: allSteps, isLoading: isLoadingSteps } = useQuery<any[]>({
        queryKey: ['progressionSteps'],
        queryFn: () => apiClient.get('/progression/steps'),
    });

    const { data: completions, isLoading: isLoadingCompletions } = useQuery<any[]>({
        queryKey: ['completions', user?.id],
        queryFn: () => apiClient.get(`/completions?mentee_id=${user?.id}`),
        enabled: !!user,
    });

    const { data: awards, isLoading: isLoadingAwards } = useQuery<any[]>({
        queryKey: ['awards', user?.id],
        queryFn: () => apiClient.get(`/awards?mentee_id=${user?.id}`),
        enabled: !!user,
    });

    const { data: badges } = useQuery<any[]>({
        queryKey: ['badges'],
        queryFn: () => apiClient.get('/badges'), // I need this endpoint
    });


    if (isLoadingSteps || isLoadingCompletions || isLoadingAwards) {
        return <div>Loading progression...</div>;
    }

    const completedStepIds = new Set(completions?.map(c => c.step_id));

    const stepsByCategory = allSteps?.reduce((acc, step) => {
        (acc[step.category] = acc[step.category] || []).push(step);
        return acc;
    }, {});

    const getBadgeName = (badgeId: string) => {
        return badges?.find(b => b.id === badgeId)?.name || 'Unknown Badge';
    }

    return (
        <div>
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>Your Badges</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-4">
                    {awards && awards.length > 0 ? (
                        awards.map(award => (
                            <div key={award.id} className="flex items-center gap-2 p-2 bg-yellow-100 text-yellow-800 rounded-md border border-yellow-300">
                                <Award className="h-5 w-5" />
                                <span className="font-semibold">{getBadgeName(award.badge_id)}</span>
                            </div>
                        ))
                    ) : (
                        <p className="text-muted-foreground">No badges earned yet. Keep jumping!</p>
                    )}
                </CardContent>
            </Card>

            {stepsByCategory && Object.entries(stepsByCategory).map(([category, steps]: [string, any[]]) => (
                <Card key={category} className="mb-6">
                    <CardHeader>
                        <CardTitle className="capitalize">{category.replace('_', ' ')} Drills</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid gap-4">
                            {steps.map(step => (
                                <div key={step.id} className="flex items-center gap-4 p-3 rounded-lg border">
                                    {completedStepIds.has(step.id) ? (
                                        <CheckCircle2 className="h-6 w-6 text-green-500" />
                                    ) : (
                                        <Circle className="h-6 w-6 text-muted-foreground" />
                                    )}
                                    <div>
                                        <h3 className="font-semibold">{step.title}</h3>
                                        <p className="text-sm text-muted-foreground">{step.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
};

export default ProgressionBoard;
