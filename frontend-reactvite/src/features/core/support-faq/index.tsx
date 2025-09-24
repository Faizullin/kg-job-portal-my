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

interface SupportFAQ {
  id: number;
  question: string;
  answer: string;
  category: string;
  is_popular: boolean;
  is_active: boolean;
  sort_order: number;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export function SupportFAQManagement() {
  const [faqs, setFaqs] = useState<SupportFAQ[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingFaq, setEditingFaq] = useState<SupportFAQ | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  // Check permissions
  const user = AuthClient.getCurrentUser();
  const canCreate = user?.permissions?.includes('core.add_supportfaq') || user?.is_superuser;
  const canEdit = user?.permissions?.includes('core.change_supportfaq') || user?.is_superuser;
  const canDelete = user?.permissions?.includes('core.delete_supportfaq') || user?.is_superuser;

  // Mock data
  const mockFaqs: SupportFAQ[] = [
    {
      id: 1,
      question: "How do I create an account?",
      answer: "You can create an account by clicking the 'Sign Up' button and following the registration process.",
      category: "Account",
      is_popular: true,
      is_active: true,
      sort_order: 1,
      view_count: 150,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
    {
      id: 2,
      question: "How do I reset my password?",
      answer: "Click on 'Forgot Password' on the login page and enter your email address to receive reset instructions.",
      category: "Account",
      is_popular: true,
      is_active: true,
      sort_order: 2,
      view_count: 89,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
    {
      id: 3,
      question: "How do I book a service?",
      answer: "Browse available services, select the one you need, and follow the booking process.",
      category: "Services",
      is_popular: false,
      is_active: true,
      sort_order: 1,
      view_count: 45,
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    },
  ];

  const filteredFaqs = mockFaqs.filter(faq =>
    faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchTerm.toLowerCase()) ||
    faq.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCreate = () => setIsCreateDialogOpen(true);
  const handleEdit = (faq: SupportFAQ) => {
    setEditingFaq(faq);
    setIsEditDialogOpen(true);
  };
  const handleDelete = (id: number) => {
    if (confirm("Are you sure you want to delete this FAQ?")) {
      console.log("Delete FAQ:", id);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Support FAQ</h1>
            <p className="text-gray-600 mt-2">
              Manage frequently asked questions and help content
            </p>
          </div>
          {canCreate && (
            <Button onClick={handleCreate}>
              <Plus className="w-4 h-4 mr-2" />
              Add FAQ
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
            placeholder="Search FAQs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Support FAQs ({filteredFaqs.length})</CardTitle>
          <CardDescription>
            Manage all frequently asked questions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Question</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Popular</TableHead>
                <TableHead>Views</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredFaqs.map((faq) => (
                <TableRow key={faq.id}>
                  <TableCell className="font-medium max-w-xs truncate">
                    {faq.question}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{faq.category}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={faq.is_popular ? "default" : "outline"}>
                      {faq.is_popular ? "Popular" : "Regular"}
                    </Badge>
                  </TableCell>
                  <TableCell>{faq.view_count}</TableCell>
                  <TableCell>
                    <Badge variant={faq.is_active ? "default" : "secondary"}>
                      {faq.is_active ? "Active" : "Inactive"}
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
                          onClick={() => handleEdit(faq)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                      )}
                      {canDelete && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleDelete(faq.id)}
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
            <DialogTitle>Create Support FAQ</DialogTitle>
            <DialogDescription>
              Add a new frequently asked question
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div>
              <Label htmlFor="question">Question</Label>
              <Input id="question" placeholder="What is your question?" />
            </div>
            
            <div>
              <Label htmlFor="answer">Answer</Label>
              <Textarea id="answer" placeholder="Provide a detailed answer..." />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="category">Category</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Account">Account</SelectItem>
                    <SelectItem value="Services">Services</SelectItem>
                    <SelectItem value="Payments">Payments</SelectItem>
                    <SelectItem value="Technical">Technical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="sort_order">Sort Order</Label>
                <Input id="sort_order" type="number" placeholder="1" />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Switch id="is_popular" />
                <Label htmlFor="is_popular">Popular FAQ</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch id="is_active" defaultChecked />
                <Label htmlFor="is_active">Active</Label>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsCreateDialogOpen(false)}>
              Create FAQ
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Support FAQ</DialogTitle>
            <DialogDescription>
              Update the frequently asked question
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div>
              <Label htmlFor="edit-question">Question</Label>
              <Input 
                id="edit-question" 
                defaultValue={editingFaq?.question}
                placeholder="What is your question?" 
              />
            </div>
            
            <div>
              <Label htmlFor="edit-answer">Answer</Label>
              <Textarea 
                id="edit-answer" 
                defaultValue={editingFaq?.answer}
                placeholder="Provide a detailed answer..." 
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-category">Category</Label>
                <Select defaultValue={editingFaq?.category}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Account">Account</SelectItem>
                    <SelectItem value="Services">Services</SelectItem>
                    <SelectItem value="Payments">Payments</SelectItem>
                    <SelectItem value="Technical">Technical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="edit-sort_order">Sort Order</Label>
                <Input 
                  id="edit-sort_order" 
                  type="number" 
                  defaultValue={editingFaq?.sort_order}
                  placeholder="1" 
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Switch 
                  id="edit-is_popular" 
                  defaultChecked={editingFaq?.is_popular}
                />
                <Label htmlFor="edit-is_popular">Popular FAQ</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch 
                  id="edit-is_active" 
                  defaultChecked={editingFaq?.is_active}
                />
                <Label htmlFor="edit-is_active">Active</Label>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsEditDialogOpen(false)}>
              Update FAQ
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
