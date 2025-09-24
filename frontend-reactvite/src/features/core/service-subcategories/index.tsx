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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Edit, Trash2, Eye } from "lucide-react";
import { AuthClient } from "@/lib/auth/auth-client";

interface ServiceSubcategory {
  id: number;
  name: string;
  description: string;
  category: number;
  category_name: string;
  is_active: boolean;
  featured: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export function ServiceSubcategoriesManagement() {
  const [subcategories, setSubcategories] = useState<ServiceSubcategory[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingSubcategory, setEditingSubcategory] = useState<ServiceSubcategory | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Check permissions
  const user = AuthClient.getCurrentUser();
  const canCreate = user?.permissions?.includes('core.add_servicesubcategory') || user?.is_superuser;
  const canEdit = user?.permissions?.includes('core.change_servicesubcategory') || user?.is_superuser;
  const canDelete = user?.permissions?.includes('core.delete_servicesubcategory') || user?.is_superuser;

  // Mock data - replace with actual API calls
  const mockSubcategories: ServiceSubcategory[] = [
    {
      id: 1,
      name: "Deep Cleaning",
      description: "Thorough deep cleaning service",
      category: 1,
      category_name: "Home Cleaning",
      is_active: true,
      featured: true,
      sort_order: 1,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
    {
      id: 2,
      name: "Regular Cleaning",
      description: "Standard weekly cleaning service",
      category: 1,
      category_name: "Home Cleaning",
      is_active: true,
      featured: false,
      sort_order: 2,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
    {
      id: 3,
      name: "Pipe Repair",
      description: "Fix leaking pipes and connections",
      category: 2,
      category_name: "Plumbing",
      is_active: true,
      featured: false,
      sort_order: 1,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
  ];

  const filteredSubcategories = mockSubcategories.filter(subcategory =>
    subcategory.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    subcategory.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    subcategory.category_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCreate = () => {
    setIsCreateDialogOpen(true);
  };

  const handleEdit = (subcategory: ServiceSubcategory) => {
    setEditingSubcategory(subcategory);
    setIsEditDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm("Are you sure you want to delete this subcategory?")) {
      // Implement delete logic
      console.log("Delete subcategory:", id);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Service Subcategories</h1>
            <p className="text-gray-600 mt-2">
              Manage specific services within categories
            </p>
          </div>
          {canCreate && (
            <Button onClick={handleCreate}>
              <Plus className="w-4 h-4 mr-2" />
              Add Subcategory
            </Button>
          )}
        </div>
      </div>

      {/* Search and Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Search & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search subcategories..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Subcategories Table */}
      <Card>
        <CardHeader>
          <CardTitle>Subcategories ({filteredSubcategories.length})</CardTitle>
          <CardDescription>
            Manage all service subcategories in the system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Featured</TableHead>
                <TableHead>Sort Order</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSubcategories.map((subcategory) => (
                <TableRow key={subcategory.id}>
                  <TableCell className="font-medium">
                    {subcategory.name}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{subcategory.category_name}</Badge>
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {subcategory.description}
                  </TableCell>
                  <TableCell>
                    <Badge variant={subcategory.is_active ? "default" : "secondary"}>
                      {subcategory.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={subcategory.featured ? "default" : "outline"}>
                      {subcategory.featured ? "Featured" : "Regular"}
                    </Badge>
                  </TableCell>
                  <TableCell>{subcategory.sort_order}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                      {canEdit && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleEdit(subcategory)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                      )}
                      {canDelete && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleDelete(subcategory.id)}
                        >
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
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Service Subcategory</DialogTitle>
            <DialogDescription>
              Add a new service subcategory to the system
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Name</Label>
                <Input id="name" placeholder="Subcategory name" />
              </div>
              <div>
                <Label htmlFor="category">Category</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Home Cleaning</SelectItem>
                    <SelectItem value="2">Plumbing</SelectItem>
                    <SelectItem value="3">Electrical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" placeholder="Subcategory description" />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="sort_order">Sort Order</Label>
                <Input id="sort_order" type="number" placeholder="1" />
              </div>
              <div className="flex items-center space-x-2">
                <Switch id="featured" />
                <Label htmlFor="featured">Featured Subcategory</Label>
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
              Create Subcategory
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Service Subcategory</DialogTitle>
            <DialogDescription>
              Update the service subcategory information
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-name">Name</Label>
                <Input 
                  id="edit-name" 
                  defaultValue={editingSubcategory?.name}
                  placeholder="Subcategory name" 
                />
              </div>
              <div>
                <Label htmlFor="edit-category">Category</Label>
                <Select defaultValue={editingSubcategory?.category.toString()}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Home Cleaning</SelectItem>
                    <SelectItem value="2">Plumbing</SelectItem>
                    <SelectItem value="3">Electrical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label htmlFor="edit-description">Description</Label>
              <Textarea 
                id="edit-description" 
                defaultValue={editingSubcategory?.description}
                placeholder="Subcategory description" 
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-sort_order">Sort Order</Label>
                <Input 
                  id="edit-sort_order" 
                  type="number" 
                  defaultValue={editingSubcategory?.sort_order}
                  placeholder="1" 
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch 
                  id="edit-featured" 
                  defaultChecked={editingSubcategory?.featured}
                />
                <Label htmlFor="edit-featured">Featured Subcategory</Label>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch 
                id="edit-is_active" 
                defaultChecked={editingSubcategory?.is_active}
              />
              <Label htmlFor="edit-is_active">Active</Label>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsEditDialogOpen(false)}>
              Update Subcategory
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
