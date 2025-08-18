import { Home, ClipboardList, Terminal, Archive, Sliders, FileText, Database, CheckCircle, Settings, AlertCircle } from 'lucide-react';

export const navItems = [
  { name: 'Dashboard', icon: Home, id: 'dashboard' },
  { name: 'Tasks', icon: ClipboardList, id: 'tasks' },
  { name: 'Logs', icon: Terminal, id: 'logs' },
  { name: 'Artifacts', icon: Archive, id: 'artifacts' },
  { name: 'Settings', icon: Sliders, id: 'settings' },
];

export const artifactTabs = [
  { id: 'requirements', name: 'Requirements', icon: FileText },
  { id: 'design', name: 'Design', icon: Database },
  { id: 'development', name: 'Development', icon: Terminal },
  { id: 'testing', name: 'Testing', icon: CheckCircle },
  { id: 'deployment', name: 'Deployment', icon: Settings },
  { id: 'maintenance', name: 'Maintenance', icon: AlertCircle },
];
