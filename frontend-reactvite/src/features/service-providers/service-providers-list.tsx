import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";

export function ServiceProvidersList() {
  const { data: providers, isLoading } = useQuery({
    queryKey: ['service-providers'],
    queryFn: async () => {
      // Mock data - replace with actual API call
      return [
        {
          id: 1,
          business_name: "CleanPro Services",
          user_name: "John Smith",
          description: "Professional cleaning services with eco-friendly products",
          average_rating: 4.8,
          total_reviews: 124,
          years_experience: 5,
          is_verified: true,
          service_areas: ["Downtown", "Midtown"],
          services: ["House Cleaning", "Office Cleaning", "Deep Cleaning"],
          is_available: true
        },
        {
          id: 2,
          business_name: "FixIt Plumbing",
          user_name: "Mike Johnson",
          description: "Licensed plumber with 10+ years experience",
          average_rating: 4.9,
          total_reviews: 89,
          years_experience: 10,
          is_verified: true,
          service_areas: ["All Areas"],
          services: ["Plumbing Repair", "Installation", "Emergency Service"],
          is_available: true
        },
        {
          id: 3,
          business_name: "Green Thumb Landscaping",
          user_name: "Sarah Wilson",
          description: "Complete landscaping and garden maintenance",
          average_rating: 4.7,
          total_reviews: 67,
          years_experience: 3,
          is_verified: false,
          service_areas: ["Suburbs", "Rural Areas"],
          services: ["Lawn Care", "Garden Design", "Tree Trimming"],
          is_available: false
        }
      ];
    }
  });

  if (isLoading) {
    return <div>Loading service providers...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Service Providers</h3>
        <div className="flex space-x-2">
          <Button variant="outline">Filter</Button>
          <Button variant="outline">Sort</Button>
        </div>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {providers?.map((provider) => (
          <Card key={provider.id}>
            <CardHeader>
              <div className="flex items-start space-x-3">
                <Avatar>
                  <AvatarImage src={`/avatars/${provider.id}.jpg`} />
                  <AvatarFallback>{provider.user_name[0]}</AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <CardTitle className="text-lg">{provider.business_name}</CardTitle>
                  <CardDescription>{provider.user_name}</CardDescription>
                  <div className="flex items-center space-x-2 mt-1">
                    {provider.is_verified && (
                      <Badge variant="secondary" className="text-xs">Verified</Badge>
                    )}
                    <Badge 
                      variant={provider.is_available ? "default" : "secondary"}
                      className="text-xs"
                    >
                      {provider.is_available ? "Available" : "Busy"}
                    </Badge>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {provider.description}
                </p>
                
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center space-x-1">
                    <span className="font-medium">{provider.average_rating}</span>
                    <span className="text-muted-foreground">({provider.total_reviews} reviews)</span>
                  </div>
                  <div className="text-muted-foreground">
                    {provider.years_experience} years exp.
                  </div>
                </div>

                <div className="space-y-2">
                  <div>
                    <p className="text-sm font-medium">Service Areas:</p>
                    <p className="text-sm text-muted-foreground">
                      {provider.service_areas.join(", ")}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Services:</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {provider.services.slice(0, 3).map((service, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {service}
                        </Badge>
                      ))}
                      {provider.services.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{provider.services.length - 3} more
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex space-x-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1" asChild>
                    <Link to={`/service-providers/${provider.id}`}>
                      View Profile
                    </Link>
                  </Button>
                  <Button size="sm" className="flex-1">
                    Contact
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

