import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';

const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

const AvailabilityEditor = () => {
    const queryClient = useQueryClient();
    const { user } = useAuth();
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    // Fetch availability
    const { data: availability, isLoading } = useQuery({
        queryKey: ['availability', user?.id],
        queryFn: () => apiClient.get(`/availability?user_id=${user?.id}`),
        enabled: !!user,
    });

    // Mutation for creating availability
    const createMutation = useMutation({
        mutationFn: (newAvailability: any) => apiClient.post('/availability', newAvailability),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['availability', user?.id] });
            setIsDialogOpen(false);
        },
    });

    // Mutation for deleting availability
    const deleteMutation = useMutation({
        mutationFn: (id: string) => apiClient.delete(`/availability/${id}`),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['availability', user?.id] });
        },
    });

    const handleAddAvailability = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const newAvailability = {
            role: user?.role,
            start_time: formData.get('start_time'),
            end_time: formData.get('end_time'),
            day_of_week: parseInt(formData.get('day_of_week') as string),
            is_recurring: true, // Simplified for now
        };
        createMutation.mutate(newAvailability);
    };

    if (isLoading) return <div>Loading availability...</div>;

    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Your Availability</CardTitle>
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                        <Button>Add New</Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Add New Availability</DialogTitle>
                        </DialogHeader>
                        <form onSubmit={handleAddAvailability} className="grid gap-4 py-4">
                            {/* This is a simplified form. A real one would have better inputs. */}
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="day_of_week" className="text-right">Day</Label>
                                <Input id="day_of_week" name="day_of_week" type="number" min="0" max="6" className="col-span-3" />
                            </div>
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="start_time" className="text-right">Start Time</Label>
                                <Input id="start_time" name="start_time" type="time" className="col-span-3" />
                            </div>
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="end_time" className="text-right">End Time</Label>
                                <Input id="end_time" name="end_time" type="time" className="col-span-3" />
                            </div>
                            <Button type="submit">Save</Button>
                        </form>
                    </DialogContent>
                </Dialog>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Day</TableHead>
                            <TableHead>Time</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead></TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {availability?.map((item: any) => (
                            <TableRow key={item.id}>
                                <TableCell>{daysOfWeek[item.day_of_week] || 'N/A'}</TableCell>
                                <TableCell>{item.start_time} - {item.end_time}</TableCell>
                                <TableCell>{item.is_recurring ? 'Recurring' : 'Single Day'}</TableCell>
                                <TableCell className="text-right">
                                    <Button variant="destructive" size="sm" onClick={() => deleteMutation.mutate(item.id)}>
                                        Delete
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
};

export default AvailabilityEditor;
