
import { ConfigDrawer } from "@/components/config-drawer";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { ThemeSwitch } from "@/components/theme-switch";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Link } from "@tanstack/react-router";
import { Briefcase, User } from "lucide-react";


export function ProfileTypeSelectionPage() {
    return (
        <>
            <Header>
                <div className="ms-auto flex items-center space-x-4">
                    <ThemeSwitch />
                    <ConfigDrawer />
                    <ProfileDropdown />
                </div>
            </Header>

            <Main>
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="w-full max-w-2xl space-y-6">
                        <div className="text-center space-y-2">
                            <h1 className="text-3xl font-bold">Добро пожаловать!</h1>
                            <p className="text-muted-foreground">
                                Выберите тип профиля, чтобы продолжить работу с платформой
                            </p>
                        </div>

                        <div className="grid gap-6 md:grid-cols-2">
                            <Card className="cursor-pointer transition-all hover:shadow-md">
                                <CardHeader>
                                    <div className="flex items-center space-x-3">
                                        <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-900/20">
                                            <User className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                                        </div>
                                        <div>
                                            <CardTitle>Клиент</CardTitle>
                                            <CardDescription>
                                                Ищу специалистов для выполнения задач
                                            </CardDescription>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-muted-foreground mb-4">
                                        Создавайте заказы, находите мастеров и управляйте своими проектами
                                    </p>
                                    <Link to="/settings/client-profile">
                                        <Button className="w-full">
                                            Настроить профиль клиента
                                        </Button>
                                    </Link>
                                </CardContent>
                            </Card>

                            <Card className="cursor-pointer transition-all hover:shadow-md">
                                <CardHeader>
                                    <div className="flex items-center space-x-3">
                                        <div className="rounded-full bg-green-100 p-3 dark:bg-green-900/20">
                                            <Briefcase className="h-6 w-6 text-green-600 dark:text-green-400" />
                                        </div>
                                        <div>
                                            <CardTitle>Мастер</CardTitle>
                                            <CardDescription>
                                                Предоставляю услуги и выполняю заказы
                                            </CardDescription>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-muted-foreground mb-4">
                                        Размещайте портфолио, получайте заказы и развивайте бизнес
                                    </p>
                                    <Link to="/settings/service-provider">
                                        <Button className="w-full">
                                            Настроить профиль мастера
                                        </Button>
                                    </Link>
                                </CardContent>
                            </Card>
                        </div>

                        <div className="text-center">
                            <p className="text-sm text-muted-foreground">
                                Вы можете настроить оба типа профиля и переключаться между ними
                            </p>
                        </div>
                    </div>
                </div>
            </Main>
        </>
    );
}