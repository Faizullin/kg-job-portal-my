import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useQuery } from "@tanstack/react-query";

interface ServiceProviderDetailProps {
  providerId: string;
}

export function ServiceProviderDetail({ providerId }: ServiceProviderDetailProps) {
  const { data: provider, isLoading } = useQuery({
    queryKey: ['service-provider', providerId],
    queryFn: async () => {
      // Mock data - replace with actual API call
      return {
        id: providerId,
        business_name: "CleanPro Services",
        user_name: "John Smith",
        description: "Professional cleaning services with eco-friendly products. We provide comprehensive cleaning solutions for residential and commercial properties.",
        average_rating: 4.8,
        total_reviews: 124,
        years_experience: 5,
        is_verified: true,
        service_areas: ["Downtown", "Midtown", "Uptown"],
        services: [
          { name: "House Cleaning", price: 80, description: "Regular house cleaning" },
          { name: "Office Cleaning", price: 120, description: "Commercial office cleaning" },
          { name: "Deep Cleaning", price: 200, description: "Thorough deep cleaning service" }
        ],
        is_available: true,
        business_license: "BL-2024-001",
        travel_radius: 25,
        availability_schedule: {
          monday: "9:00 AM - 6:00 PM",
          tuesday: "9:00 AM - 6:00 PM",
          wednesday: "9:00 AM - 6:00 PM",
          thursday: "9:00 AM - 6:00 PM",
          friday: "9:00 AM - 6:00 PM",
          saturday: "10:00 AM - 4:00 PM",
          sunday: "Closed"
        },
        recent_reviews: [
          {
            id: 1,
            client_name: "Alice Johnson",
            rating: 5,
            comment: "Excellent service! Very professional and thorough.",
            date: "2024-01-10"
          },
          {
            id: 2,
            client_name: "Bob Smith",
            rating: 4,
            comment: "Good work, arrived on time and cleaned well.",
            date: "2024-01-08"
          }
        ]
      };
    }
  });

  if (isLoading) {
    return <div>Loading provider details...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start space-x-4">
        <Avatar className="h-20 w-20">
          <AvatarImage src={`/avatars/${provider?.id}.jpg`} />
          <AvatarFallback className="text-lg">{provider?.user_name?.[0]}</AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold">{provider?.business_name}</h2>
              <p className="text-muted-foreground">{provider?.user_name}</p>
              <div className="flex items-center space-x-2 mt-2">
                {provider?.is_verified && (
                  <Badge variant="secondary">Verified</Badge>
                )}
                <Badge 
                  variant={provider?.is_available ? "default" : "secondary"}
                >
                  {provider?.is_available ? "Available" : "Busy"}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{provider?.average_rating}</div>
              <div className="text-sm text-muted-foreground">
                {provider?.total_reviews} reviews
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>About</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">{provider?.description}</p>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Experience:</span>
                <span className="text-sm">{provider?.years_experience} years</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium">Business License:</span>
                <span className="text-sm">{provider?.business_license}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium">Travel Radius:</span>
                <span className="text-sm">{provider?.travel_radius} km</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Service Areas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {provider?.service_areas?.map((area, index) => (
                <Badge key={index} variant="outline">{area}</Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Services Offered</CardTitle>
          <CardDescription>Available services and pricing</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {provider?.services?.map((service, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">{service.name}</h4>
                    <p className="text-sm text-muted-foreground">{service.description}</p>
                  </div>
                  <div className="text-lg font-semibold">${service.price}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Availability</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {Object.entries(provider?.availability_schedule || {}).map(([day, hours]) => (
              <div key={day} className="flex justify-between">
                <span className="font-medium capitalize">{day}:</span>
                <span className="text-muted-foreground">{hours}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Reviews</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {provider?.recent_reviews?.map((review) => (
              <div key={review.id} className="border-b pb-4 last:border-b-0">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-medium">{review.client_name}</h4>
                    <div className="flex items-center space-x-1">
                      {[...Array(5)].map((_, i) => (
                        <span key={i} className={i < review.rating ? "text-yellow-400" : "text-gray-300"}>
                          ★
                        </span>
                      ))}
                    </div>
                  </div>
                  <span className="text-sm text-muted-foreground">{review.date}</span>
                </div>
                <p className="text-sm text-muted-foreground">{review.comment}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex space-x-4">
        <Button className="flex-1">Contact Provider</Button>
        <Button variant="outline" className="flex-1">View All Reviews</Button>
      </div>
    </div>
  );
}

