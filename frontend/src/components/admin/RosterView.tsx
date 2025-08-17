import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Calendar as CalendarIcon } from 'lucide-react';

import { cn } from '@/lib/utils';
import { apiClient } from '@/api/client';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const RosterView = () => {
    const [date, setDate] = useState<Date | undefined>(new Date());
    const formattedDate = date ? format(date, 'yyyy-MM-dd') : '';

    const { data: roster, isLoading } = useQuery<any[]>({
        queryKey: ['roster', formattedDate],
        queryFn: () => apiClient.get(`/admin/roster?date=${formattedDate}`),
        enabled: !!date,
    });

    return (
        <Card>
            <CardHeader>
                <CardTitle>Daily Roster</CardTitle>
                <CardDescription>View assignments for a specific day.</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="grid gap-4">
                    <div>
                        <Popover>
                            <PopoverTrigger asChild>
                                <Button
                                    variant={"outline"}
                                    className={cn("w-[280px] justify-start text-left font-normal", !date && "text-muted-foreground")}
                                >
                                    <CalendarIcon className="mr-2 h-4 w-4" />
                                    {date ? format(date, "PPP") : <span>Pick a date</span>}
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0">
                                <Calendar mode="single" selected={date} onSelect={setDate} initialFocus />
                            </PopoverContent>
                        </Popover>
                    </div>

                    {isLoading && <div>Loading roster...</div>}

                    <div className="grid gap-4">
                        {roster && roster.length > 0 ? (
                            roster.map(rosterItem => (
                                <div key={rosterItem.session_block.id}>
                                    <h3 className="font-semibold text-lg mt-4 mb-2">
                                        Session: {rosterItem.session_block.start_time} - {rosterItem.session_block.end_time}
                                    </h3>
                                    {rosterItem.assignments.length > 0 ? (
                                        <Table>
                                            <TableHeader>
                                                <TableRow>
                                                    <TableHead>Mentor</TableHead>
                                                    <TableHead>Mentee</TableHead>
                                                    <TableHead>Status</TableHead>
                                                </TableRow>
                                            </TableHeader>
                                            <TableBody>
                                                {rosterItem.assignments.map((assignment: any) => (
                                                    <TableRow key={assignment.id}>
                                                        <TableCell>{assignment.mentor.name}</TableCell>
                                                        <TableCell>{assignment.mentee.name}</TableCell>
                                                        <TableCell>{assignment.status}</TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    ) : (
                                        <p className="text-sm text-muted-foreground">No assignments for this session.</p>
                                    )}
                                </div>
                            ))
                        ) : (
                            !isLoading && <p>No sessions or assignments for this date.</p>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default RosterView;
