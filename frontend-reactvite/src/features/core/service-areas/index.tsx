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
import { Switch } from "@/components/ui/switch";
import { Plus, Edit, Trash2, Eye } from "lucide-react";
import { AuthClient } from "@/lib/auth/auth-client";

interface ServiceArea {
  id: number;
  name: string;
  city: string;
  state: string;
  country: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export function ServiceAreasManagement() {
  const [areas, setAreas] = useState<ServiceArea[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingArea, setEditingArea] = useState<ServiceArea | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  // Check permissions
  const user = AuthClient.getCurrentUser();
  const canCreate = user?.permissions?.includes('core.add_servicearea') || user?.is_superuser;
  const canEdit = user?.permissions?.includes('core.change_servicearea') || user?.is_superuser;
  const canDelete = user?.permissions?.includes('core.delete_servicearea') || user?.is_superuser;

  // Mock data
  const mockAreas: ServiceArea[] = [
    {
      id: 1,
      name: "Downtown",
      city: "New York",
      state: "NY",
      country: "USA",
      is_active: true,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
    {
      id: 2,
      name: "Manhattan",
      city: "New York",
      state: "NY", 
      country: "USA",
      is_active: true,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
  ];

  const filteredAreas = mockAreas.filter(area =>
    area.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    area.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
    area.state.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCreate = () => setIsCreateDialogOpen(true);
  const handleEdit = (area: ServiceArea) => {
    setEditingArea(area);
    setIsEditDialogOpen(true);
  };
  const handleDelete = (id: number) => {
    if (confirm("Are you sure you want to delete this area?")) {
      console.log("Delete area:", id);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Service Areas</h1>
            <p className="text-gray-600 mt-2">Manage geographic service areas</p>
          </div>
          {canCreate && (
            <Button onClick={handleCreate}>
              <Plus className="w-4 h-4 mr-2" />
              Add Area
            </Button>
          )}
        </div>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Search & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <Input
            placeholder="Search areas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Service Areas ({filteredAreas.length})</CardTitle>
          <CardDescription>Manage all service areas in the system</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>City</TableHead>
                <TableHead>State</TableHead>
                <TableHead>Country</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAreas.map((area) => (
                <TableRow key={area.id}>
                  <TableCell className="font-medium">{area.name}</TableCell>
                  <TableCell>{area.city}</TableCell>
                  <TableCell>{area.state}</TableCell>
                  <TableCell>{area.country}</TableCell>
                  <TableCell>
                    <Badge variant={area.is_active ? "default" : "secondary"}>
                      {area.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                      {canEdit && (
                        <Button variant="outline" size="sm" onClick={() => handleEdit(area)}>
                          <Edit className="w-4 h-4" />
                        </Button>
                      )}
                      {canDelete && (
                        <Button variant="outline" size="sm" onClick={() => handleDelete(area.id)}>
                          <Trash2 className="w-4 h-4" />
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

      {/* Create Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Service Area</DialogTitle>
            <DialogDescription>Add a new service area to the system</DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Name</Label>
                <Input id="name" placeholder="Area name" />
              </div>
              <div>
                <Label htmlFor="city">City</Label>
                <Input id="city" placeholder="City name" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="state">State</Label>
                <Input id="state" placeholder="State" />
              </div>
              <div>
                <Label htmlFor="country">Country</Label>
                <Input id="country" placeholder="Country" />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Switch id="is_active" defaultChecked />
              <Label htmlFor="is_active">Active</Label>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsCreateDialogOpen(false)}>
              Create Area
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Service Area</DialogTitle>
            <DialogDescription>Update the service area information</DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-name">Name</Label>
                <Input id="edit-name" defaultValue={editingArea?.name} placeholder="Area name" />
              </div>
              <div>
                <Label htmlFor="edit-city">City</Label>
                <Input id="edit-city" defaultValue={editingArea?.city} placeholder="City name" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-state">State</Label>
                <Input id="edit-state" defaultValue={editingArea?.state} placeholder="State" />
              </div>
              <div>
                <Label htmlFor="edit-country">Country</Label>
                <Input id="edit-country" defaultValue={editingArea?.country} placeholder="Country" />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Switch id="edit-is_active" defaultChecked={editingArea?.is_active} />
              <Label htmlFor="edit-is_active">Active</Label>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsEditDialogOpen(false)}>
              Update Area
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
