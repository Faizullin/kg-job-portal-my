import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Edit, Eye } from "lucide-react";
import { AuthClient } from "@/lib/auth/auth-client";

interface SystemSetting {
  id: number;
  key: string;
  value: string;
  description: string;
  setting_type: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export function SystemSettingsManagement() {
  const [settings, setSettings] = useState<SystemSetting[]>([]);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingSetting, setEditingSetting] = useState<SystemSetting | null>(null);

  // Check permissions
  const user = AuthClient.getCurrentUser();
  const canEdit = user?.permissions?.includes('core.change_systemsettings') || user?.is_superuser;

  // Mock data
  const mockSettings: SystemSetting[] = [
    {
      id: 1,
      key: "site_name",
      value: "KG Job Portal",
      description: "The name of the website",
      setting_type: "string",
      is_active: true,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
    {
      id: 2,
      key: "default_commission_rate",
      value: "10.0",
      description: "Default commission rate for services",
      setting_type: "float",
      is_active: true,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
    {
      id: 3,
      key: "max_file_upload_size",
      value: "10485760",
      description: "Maximum file upload size in bytes (10MB)",
      setting_type: "integer",
      is_active: true,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
  ];

  const handleEdit = (setting: SystemSetting) => {
    setEditingSetting(setting);
    setIsEditDialogOpen(true);
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>
          <p className="text-gray-600 mt-2">
            Configure system-wide settings and parameters
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Settings ({mockSettings.length})</CardTitle>
          <CardDescription>
            Manage all system configuration settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Key</TableHead>
                <TableHead>Value</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockSettings.map((setting) => (
                <TableRow key={setting.id}>
                  <TableCell className="font-medium">{setting.key}</TableCell>
                  <TableCell className="max-w-xs truncate">{setting.value}</TableCell>
                  <TableCell className="max-w-xs truncate">{setting.description}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{setting.setting_type}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={setting.is_active ? "default" : "secondary"}>
                      {setting.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                      {canEdit && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleEdit(setting)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit System Setting</DialogTitle>
            <DialogDescription>
              Update the system setting value
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div>
              <Label htmlFor="edit-key">Key</Label>
              <Input 
                id="edit-key" 
                defaultValue={editingSetting?.key}
                disabled
                className="bg-gray-50"
              />
            </div>
            
            <div>
              <Label htmlFor="edit-description">Description</Label>
              <Textarea 
                id="edit-description" 
                defaultValue={editingSetting?.description}
                disabled
                className="bg-gray-50"
              />
            </div>
            
            <div>
              <Label htmlFor="edit-value">Value</Label>
              <Input 
                id="edit-value" 
                defaultValue={editingSetting?.value}
                placeholder="Enter new value"
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch 
                id="edit-is_active" 
                defaultChecked={editingSetting?.is_active}
              />
              <Label htmlFor="edit-is_active">Active</Label>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsEditDialogOpen(false)}>
              Update Setting
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
