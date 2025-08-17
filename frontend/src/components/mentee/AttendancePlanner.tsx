import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Calendar as CalendarIcon } from 'lucide-react';

import { cn } from '@/lib/utils';
import { apiClient } from '@/api/client';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const AttendancePlanner = () => {
    const queryClient = useQueryClient();
    const [date, setDate] = useState<Date | undefined>(new Date());

    const formattedDate = date ? format(date, 'yyyy-MM-dd') : '';

    const { data: sessions, isLoading } = useQuery<any[]>({
        queryKey: ['sessions', formattedDate],
        queryFn: () => apiClient.get(`/sessions?date=${formattedDate}`),
        enabled: !!date,
    });

    const attendanceMutation = useMutation({
        mutationFn: (sessionBlockId: string) => apiClient.post('/attendance', { session_block_id: sessionBlockId }),
        onSuccess: () => {
            alert('Successfully signed up for session!');
            // Optionally refetch user's attendance requests
        },
        onError: (error: any) => {
            alert(`Error: ${error.message}`);
        }
    });

    return (
        <Card>
            <CardHeader>
                <CardTitle>Plan Your Attendance</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid gap-4">
                    <div>
                        <Popover>
                            <PopoverTrigger asChild>
                                <Button
                                    variant={"outline"}
                                    className={cn(
                                        "w-[280px] justify-start text-left font-normal",
                                        !date && "text-muted-foreground"
                                    )}
                                >
                                    <CalendarIcon className="mr-2 h-4 w-4" />
                                    {date ? format(date, "PPP") : <span>Pick a date</span>}
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0">
                                <Calendar
                                    mode="single"
                                    selected={date}
                                    onSelect={setDate}
                                    initialFocus
                                />
                            </PopoverContent>
                        </Popover>
                    </div>

                    {isLoading && <div>Loading sessions...</div>}

                    <div className="grid gap-2">
                        {sessions && sessions.length > 0 ? (
                            sessions.map(session => (
                                <div key={session.id} className="flex justify-between items-center p-2 border rounded-md">
                                    <span>{session.start_time} - {session.end_time}</span>
                                    <Button size="sm" onClick={() => attendanceMutation.mutate(session.id)}>
                                        Sign Up
                                    </Button>
                                </div>
                            ))
                        ) : (
                            !isLoading && <p>No sessions available for this date.</p>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default AttendancePlanner;
