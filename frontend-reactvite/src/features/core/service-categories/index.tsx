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
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Plus, Edit, Trash2, Eye } from "lucide-react";
import { AuthClient } from "@/lib/auth/auth-client";

interface ServiceCategory {
  id: number;
  name: string;
  description: string;
  icon: string;
  color: string;
  is_active: boolean;
  featured: boolean;
  sort_order: number;
  commission_rate: number;
  slug: string;
  created_at: string;
  updated_at: string;
}

export function ServiceCategoriesManagement() {
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<ServiceCategory | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Check permissions
  const user = AuthClient.getCurrentUser();
  const canCreate = user?.permissions?.includes('core.add_servicecategory') || user?.is_superuser;
  const canEdit = user?.permissions?.includes('core.change_servicecategory') || user?.is_superuser;
  const canDelete = user?.permissions?.includes('core.delete_servicecategory') || user?.is_superuser;

  // Mock data - replace with actual API calls
  const mockCategories: ServiceCategory[] = [
    {
      id: 1,
      name: "Home Cleaning",
      description: "Professional home cleaning services",
      icon: "home",
      color: "#4CAF50",
      is_active: true,
      featured: true,
      sort_order: 1,
      commission_rate: 10.0,
      slug: "home-cleaning",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
    {
      id: 2,
      name: "Plumbing",
      description: "Plumbing repair and installation services",
      icon: "wrench",
      color: "#2196F3",
      is_active: true,
      featured: false,
      sort_order: 2,
      commission_rate: 12.0,
      slug: "plumbing",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
  ];

  const filteredCategories = mockCategories.filter(category =>
    category.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    category.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCreate = () => {
    setIsCreateDialogOpen(true);
  };

  const handleEdit = (category: ServiceCategory) => {
    setEditingCategory(category);
    setIsEditDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm("Are you sure you want to delete this category?")) {
      // Implement delete logic
      console.log("Delete category:", id);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Service Categories</h1>
            <p className="text-gray-600 mt-2">
              Manage service categories and their configurations
            </p>
          </div>
          {canCreate && (
            <Button onClick={handleCreate}>
              <Plus className="w-4 h-4 mr-2" />
              Add Category
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
                placeholder="Search categories..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Categories Table */}
      <Card>
        <CardHeader>
          <CardTitle>Categories ({filteredCategories.length})</CardTitle>
          <CardDescription>
            Manage all service categories in the system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Featured</TableHead>
                <TableHead>Commission</TableHead>
                <TableHead>Sort Order</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredCategories.map((category) => (
                <TableRow key={category.id}>
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: category.color }}
                      />
                      {category.name}
                    </div>
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {category.description}
                  </TableCell>
                  <TableCell>
                    <Badge variant={category.is_active ? "default" : "secondary"}>
                      {category.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={category.featured ? "default" : "outline"}>
                      {category.featured ? "Featured" : "Regular"}
                    </Badge>
                  </TableCell>
                  <TableCell>{category.commission_rate}%</TableCell>
                  <TableCell>{category.sort_order}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                      {canEdit && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleEdit(category)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                      )}
                      {canDelete && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleDelete(category.id)}
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
            <DialogTitle>Create Service Category</DialogTitle>
            <DialogDescription>
              Add a new service category to the system
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Name</Label>
                <Input id="name" placeholder="Category name" />
              </div>
              <div>
                <Label htmlFor="icon">Icon</Label>
                <Input id="icon" placeholder="Icon name" />
              </div>
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" placeholder="Category description" />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="color">Color</Label>
                <Input id="color" type="color" defaultValue="#4CAF50" />
              </div>
              <div>
                <Label htmlFor="commission">Commission Rate (%)</Label>
                <Input id="commission" type="number" placeholder="10.0" />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="sort_order">Sort Order</Label>
                <Input id="sort_order" type="number" placeholder="1" />
              </div>
              <div className="flex items-center space-x-2">
                <Switch id="featured" />
                <Label htmlFor="featured">Featured Category</Label>
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
              Create Category
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Service Category</DialogTitle>
            <DialogDescription>
              Update the service category information
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-name">Name</Label>
                <Input 
                  id="edit-name" 
                  defaultValue={editingCategory?.name}
                  placeholder="Category name" 
                />
              </div>
              <div>
                <Label htmlFor="edit-icon">Icon</Label>
                <Input 
                  id="edit-icon" 
                  defaultValue={editingCategory?.icon}
                  placeholder="Icon name" 
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="edit-description">Description</Label>
              <Textarea 
                id="edit-description" 
                defaultValue={editingCategory?.description}
                placeholder="Category description" 
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-color">Color</Label>
                <Input 
                  id="edit-color" 
                  type="color" 
                  defaultValue={editingCategory?.color || "#4CAF50"} 
                />
              </div>
              <div>
                <Label htmlFor="edit-commission">Commission Rate (%)</Label>
                <Input 
                  id="edit-commission" 
                  type="number" 
                  defaultValue={editingCategory?.commission_rate}
                  placeholder="10.0" 
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-sort_order">Sort Order</Label>
                <Input 
                  id="edit-sort_order" 
                  type="number" 
                  defaultValue={editingCategory?.sort_order}
                  placeholder="1" 
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch 
                  id="edit-featured" 
                  defaultChecked={editingCategory?.featured}
                />
                <Label htmlFor="edit-featured">Featured Category</Label>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch 
                id="edit-is_active" 
                defaultChecked={editingCategory?.is_active}
              />
              <Label htmlFor="edit-is_active">Active</Label>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsEditDialogOpen(false)}>
              Update Category
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
