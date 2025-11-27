import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plus, ArrowUpDown } from 'lucide-react';
import { TaskDialog } from '@/components/TaskDialog';

export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  owner_id: string;
  owner_name: string;
  created_at: string;
}

// Mock tasks data
const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Implement user authentication',
    description: 'Set up JWT-based authentication for the API',
    status: 'in_progress',
    priority: 'high',
    owner_id: '1',
    owner_name: 'John Employee',
    created_at: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    title: 'Design database schema',
    description: 'Create ERD and implement PostgreSQL schema',
    status: 'completed',
    priority: 'high',
    owner_id: '1',
    owner_name: 'John Employee',
    created_at: '2024-01-14T09:00:00Z',
  },
  {
    id: '3',
    title: 'Write API documentation',
    description: 'Document all REST endpoints using Swagger',
    status: 'pending',
    priority: 'medium',
    owner_id: '2',
    owner_name: 'Sarah Leader',
    created_at: '2024-01-16T11:00:00Z',
  },
];

export default function TasksDashboard() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>(mockTasks);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<Task['priority'] | 'all'>('all');

  const isTeamLeader = user?.role === 'team_leader';
  
  let filteredTasks = isTeamLeader 
    ? tasks 
    : tasks.filter(task => task.owner_id === user?.id);
  
  if (priorityFilter !== 'all') {
    filteredTasks = filteredTasks.filter(task => task.priority === priorityFilter);
  }

  const handleCreateTask = () => {
    setSelectedTask(null);
    setIsDialogOpen(true);
  };

  const handleEditTask = (task: Task) => {
    setSelectedTask(task);
    setIsDialogOpen(true);
  };

  const handleSaveTask = (taskData: Partial<Task>) => {
    if (selectedTask) {
      // Update existing task
      setTasks(tasks.map(t => t.id === selectedTask.id ? { ...t, ...taskData } : t));
    } else {
      // Create new task
      const newTask: Task = {
        id: String(tasks.length + 1),
        title: taskData.title!,
        description: taskData.description!,
        status: taskData.status || 'pending',
        priority: taskData.priority || 'medium',
        owner_id: user?.id || '1',
        owner_name: user?.name || 'Unknown',
        created_at: new Date().toISOString(),
      };
      setTasks([...tasks, newTask]);
    }
    setIsDialogOpen(false);
  };

  const handleDeleteTask = (taskId: string) => {
    setTasks(tasks.filter(t => t.id !== taskId));
  };

  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed': return 'bg-green-500 text-white';
      case 'in_progress': return 'bg-blue-600 text-white';
      default: return 'bg-gray-300 text-gray-700';
    }
  };

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'high': return 'bg-red-500 text-white';
      case 'medium': return 'bg-yellow-500 text-white';
      default: return 'bg-gray-300 text-gray-700';
    }
  };

  const getPriorityLabel = (priority: Task['priority']) => {
    switch (priority) {
      case 'high': return 'High';
      case 'medium': return 'Medium';
      default: return 'Low';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-6 py-8">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1">Tasks Dashboard</h1>
            <p className="text-gray-500 text-sm">Manage all tasks</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setPriorityFilter(priorityFilter === 'high' ? 'all' : 'high')}
                className={`rounded-full text-xs px-4 py-1 h-8 ${priorityFilter === 'high' ? 'bg-purple-700 text-white hover:bg-purple-800 border-purple-700' : 'border-gray-300 hover:bg-gray-100'}`}
              >
                High Priority
              </Button>
              <Button
                variant="outline"
                onClick={() => setPriorityFilter(priorityFilter === 'medium' ? 'all' : 'medium')}
                className={`rounded-full text-xs px-4 py-1 h-8 ${priorityFilter === 'medium' ? 'bg-purple-700 text-white hover:bg-purple-800 border-purple-700' : 'border-gray-300 hover:bg-gray-100'}`}
              >
                Medium Priority
              </Button>
              <Button
                variant="outline"
                onClick={() => setPriorityFilter(priorityFilter === 'low' ? 'all' : 'low')}
                className={`rounded-full text-xs px-4 py-1 h-8 ${priorityFilter === 'low' ? 'bg-purple-700 text-white hover:bg-purple-800 border-purple-700' : 'border-gray-300 hover:bg-gray-100'}`}
              >
                Low Priority
              </Button>
            </div>
            <Button variant="outline" size="icon" className="h-10 w-10 rounded-lg border-gray-300">
              <ArrowUpDown className="h-4 w-4" />
            </Button>
            <Button 
              onClick={handleCreateTask}
              className="bg-purple-700 hover:bg-purple-800 text-white px-6 rounded-lg"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Task
            </Button>
          </div>
        </div>

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {filteredTasks.map(task => (
            <Card 
              key={task.id} 
              className="bg-white hover:shadow-xl transition-shadow cursor-pointer border border-gray-200 rounded-2xl overflow-hidden"
              onClick={() => handleEditTask(task)}
            >
              <div className="p-5">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-base font-semibold text-gray-900 flex-1">{task.title}</h3>
                  <Badge className={`${getPriorityColor(task.priority)} rounded-md px-3 py-1 text-xs font-semibold ml-3 shrink-0`}>
                    {getPriorityLabel(task.priority)}
                  </Badge>
                </div>
                
                <p className="text-xs text-gray-500 mb-4">
                  {task.description.length > 60 ? `${task.description.substring(0, 60)}...` : task.description} 
                  <span className="text-gray-400 ml-1">View More</span>
                </p>

                <Badge className={`${getStatusColor(task.status)} rounded-md px-3 py-1.5 text-xs font-semibold mb-4 inline-block`}>
                  {task.status === 'in_progress' ? 'In Progress' : task.status === 'completed' ? 'Completed' : 'Pending'}
                </Badge>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between text-gray-600">
                    <span>Assigned To:</span>
                    <span className="font-medium text-gray-900">{task.owner_name}</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>Assigned On:</span>
                    <span className="font-medium text-gray-900">{new Date(task.created_at).toLocaleDateString('en-US', { day: '2-digit', month: '2-digit', year: 'numeric' })}</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>Due Date:</span>
                    <span className="font-medium text-gray-900">{new Date(task.created_at).toLocaleDateString('en-US', { day: '2-digit', month: '2-digit', year: 'numeric' })}</span>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {filteredTasks.length === 0 && (
          <Card className="text-center py-12 bg-white">
            <div className="p-6">
              <p className="text-gray-600">No tasks found. Create your first task to get started.</p>
            </div>
          </Card>
        )}
      </div>

      <TaskDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        task={selectedTask}
        onSave={handleSaveTask}
        onDelete={handleDeleteTask}
        isTeamLeader={isTeamLeader}
      />
    </div>
  );
}
