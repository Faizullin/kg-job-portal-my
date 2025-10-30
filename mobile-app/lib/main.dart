import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_web_plugins/url_strategy.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'core/di/injection_container.dart';
import 'features/login/logic/bloc/auth_bloc.dart';
import 'features/login/logic/bloc/auth_event.dart';
import 'features/login/logic/bloc/auth_state.dart';
import 'core/widgets/main_layout.dart';
import 'features/profile/screens/profile_screen.dart';
import 'features/masters/screens/masters_screen.dart';
import 'features/tasks/screens/tasks_screen.dart';
import 'features/otzyvy/screens/otzyvy_screen.dart';
import 'features/help/screens/help_screen.dart';
import 'features/splash/screens/splash_screen.dart';
import 'features/login/screens/login_screen.dart';
import 'features/register/screens/register_screen.dart';
import 'features/first_impression/screens/first_impression_screen.dart';
import 'features/home/screens/home_screen.dart';
import 'features/language/screens/language_screen.dart';
import 'features/about_app/screens/about_app_screen.dart';
import 'features/edit_profile/screens/edit_profile_screen.dart';
import 'features/term_of_service/screens/term_of_service_screen.dart';
import 'features/what_you_want/screens/what_you_want_screen.dart';
import 'features/which_service_want/screens/which_service_want_screen.dart';
import 'features/razreshenie/screens/razreshenie_screen.dart';
import 'features/chats/screens/chats_list_screen.dart';
import 'features/chats/screens/chat_detail_screen.dart';
import 'features/chats/models/chat_model.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Инициализация Firebase
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
  // Инициализация зависимостей
  InjectionContainer.instance.init();
  
  GoRouter.optionURLReflectsImperativeAPIs = true;
  usePathUrlStrategy();

  runApp(MyApp());
}

class MyApp extends StatefulWidget {
  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  late GoRouter _router;

  @override
  void initState() {
    super.initState();
    _router = _createRouter();
  }

  GoRouter _createRouter() {
    return GoRouter(
      initialLocation: '/splash',
      // redirect: (context, state) {
      //   // Проверяем состояние аутентификации
      //   // final authBloc = context.read<AuthBloc>();
      //   
      //   // Если пользователь авторизован и находится на экранах входа
      //   // if (authBloc.state is AuthAuthenticated) {
      //   //   if (state.uri.path == '/login' || 
      //   //       state.uri.path == '/register' || 
      //   //       state.uri.path == '/first_impression') {
      //   //     // return '/'; // Перенаправляем на главный экран
      //   //     return '/chats'; // Перенаправляем на экран чатов
      //   //   }
      //   // }
      //   
      //   // Если пользователь не авторизован и пытается попасть на защищенные экраны
      //   // if (authBloc.state is AuthUnauthenticated) {
      //   //   if (state.uri.path == '/') {
      //   //     return '/login'; // Перенаправляем на экран входа
      //   //   }
      //   // }
      //   
      //   // return null; // Не перенаправляем
      //   // Открываем чаты напрямую без проверки аутентификации
      //   return null;
      // },
      routes: [
        GoRoute(
          path: '/splash',
          builder: (context, state) => SplashScreen(),
        ),
        GoRoute(
          path: '/login',
          builder: (context, state) => LoginScreen(),
        ),
        GoRoute(
          path: '/register',
          builder: (context, state) => RegisterScreen(),
        ),
        GoRoute(
          path: '/first_impression',
          builder: (context, state) => FirstImpressionScreen(),
        ),
        GoRoute(
          path: '/home',
          builder: (context, state) => HomeScreen(),
        ),
        GoRoute(
          path: '/',
          builder: (context, state) => MainLayout(),
        ),
        GoRoute(
          path: '/profile',
          builder: (context, state) => ProfileScreen(),
        ),
        GoRoute(
          path: '/masters',
          builder: (context, state) => MastersScreen(),
        ),
        GoRoute(
          path: '/tasks',
          builder: (context, state) => TasksScreen(),
        ),
        GoRoute(
          path: '/otzyvy',
          builder: (context, state) => OtzyvyScreen(),
        ),
        GoRoute(
          path: '/help',
          builder: (context, state) => HelpScreen(),
        ),
        GoRoute(
          path: '/language',
          builder: (context, state) => LanguageScreen(),
        ),
        GoRoute(
          path: '/about_app',
          builder: (context, state) => AboutAppScreen(),
        ),
        GoRoute(
          path: '/edit_profile',
          builder: (context, state) => EditProfileScreen(),
        ),
        GoRoute(
          path: '/term_of_service',
          builder: (context, state) => TermOfServiceScreen(),
        ),
        GoRoute(
          path: '/what_you_want',
          builder: (context, state) => WhatYouWantScreen(),
        ),
        GoRoute(
          path: '/which_service_want',
          builder: (context, state) => WhichServiceWantScreen(),
        ),
        GoRoute(
          path: '/razreshenie',
          builder: (context, state) => RazreshenieScreen(),
        ),
        GoRoute(
          path: '/chats',
          builder: (context, state) => ChatsListScreen(),
        ),
        GoRoute(
          path: '/chat/:chatId',
          builder: (context, state) {
            final chat = state.extra as ChatModel?;
            if (chat != null) {
              return ChatDetailScreen(chat: chat);
            }
            return const Scaffold(
              body: Center(child: Text('Chat not found')),
            );
          },
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider<AuthBloc>(
      create: (context) => InjectionContainer.instance.authBloc
        ..add(const AuthInitialized()),
      child: MaterialApp.router(
      debugShowCheckedModeBanner: false,
      title: 'Master KG',
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.ltr,
          child: child!,
        );
      },
      localizationsDelegates: [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('ky'),
        Locale('ru'),
      ],
      theme: ThemeData(
        brightness: Brightness.light,
        useMaterial3: false,
        primarySwatch: Colors.blue,
        primaryColor: Color(0xFF2563EB),
        scaffoldBackgroundColor: Color(0xFFF1F4F8),
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        useMaterial3: false,
        primarySwatch: Colors.blue,
        primaryColor: Color(0xFF4B39EF),
        scaffoldBackgroundColor: Color(0xFF1D2428),
      ),
      routerConfig: _router,
      ),
    );
  }
}




