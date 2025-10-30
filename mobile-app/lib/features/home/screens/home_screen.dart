import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import '../logic/bloc/home_bloc.dart';
import '../logic/bloc/home_event.dart';
import '../logic/bloc/home_state.dart';
import '../logic/data/home_repository.dart';
import '../logic/data/home_data_source.dart';
import '../widgets/home_search_bar.dart';
import '../widgets/service_card.dart';
import '../widgets/service_item.dart';
import '../widgets/specialist_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => HomeBloc(
        repository: HomeRepositoryImpl(
          dataSource: HomeDataSourceImpl(),
        ),
      )..add(LoadHomeDataEvent()),
      child: const HomeView(),
    );
  }
}

class HomeView extends StatelessWidget {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: theme.primaryColor,
        automaticallyImplyLeading: false,
        elevation: 0.0,
        toolbarHeight: 50.0, // Фиксированная высота AppBar
        title: Row(
          children: [
            // Profile Image
            Container(
              width: 45.0,
              height: 45.0,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
              ),
              child: ClipOval(
                child: Image.network(
                  'https://picsum.photos/seed/656/600',
                  fit: BoxFit.cover,
                ),
              ),
            ),
            SizedBox(width: 4.0),
            // User Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.location_on_sharp,
                        color: Colors.white,
                        size: 14.0,
                      ),
                      SizedBox(width: 1.0),
                      Text(
                        'Алматы',
                        style: GoogleFonts.inter(
                          color: Colors.white,
                          fontSize: 10.0,
                          fontWeight: FontWeight.normal,
                        ),
                      ),
                    ],
                  ),
                    Text(
                      'Добрый день, Нурдаулет',
                      style: GoogleFonts.roboto(
                        color: Colors.white,
                        fontWeight: FontWeight.w400,
                        fontSize: 14.0,
                      ),
                    ),
                ],
              ),
            ),
            // Action Icons
            Row(
              children: [
                Icon(
                  Icons.notifications,
                  color: Colors.white,
                  size: 21.0,
                ),
                SizedBox(width: 6.0),
                Icon(
                  Icons.menu,
                  color: Colors.white,
                  size: 21.0,
                ),
              ],
            ),
          ],
        ),
      ),
      body: BlocBuilder<HomeBloc, HomeState>(
        builder: (context, state) {
          if (state is HomeLoadingState) {
            return Center(child: CircularProgressIndicator());
          }
          
          if (state is HomeErrorState) {
            return Center(
              child: Text(
                state.message,
                style: GoogleFonts.roboto(fontSize: 16.0),
              ),
            );
          }
          
          return Column(
            children: [
              // Фиксированный синий контейнер сверху
              Container(
                width: double.infinity,
                height: 72.0,
                decoration: BoxDecoration(
                  color: theme.primaryColor,
                ),
                child: Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Search Bar
                      HomeSearchBar(),
                    ],
                  ),
                ),
              ),
              // Скроллируемый контент
              Expanded(
                child: RefreshIndicator(
                  onRefresh: () async {
                    context.read<HomeBloc>().add(RefreshHomeDataEvent());
                  },
                  child: SingleChildScrollView(
                    child: Column(
                      children: [
                        // Interest Section
                        Align(
                          alignment: Alignment.centerLeft,
                          child: Padding(
                            padding: EdgeInsets.only(left: 16.0, top: 16.0),
                            child: Text(
                              'Вас может заинтересовать',
                              style: GoogleFonts.roboto(
                                fontWeight: FontWeight.w600,
                                fontSize: 24.0,
                                color: Color(0xFF101828),
                              ),
                            ),
                          ),
                        ),
                        // Horizontal Services List
                        Container(
                          height: 180.0,
                          padding: EdgeInsets.symmetric(vertical: 8.0),
                          child: ListView(
                            padding: EdgeInsets.only(left: 16.0),
                            scrollDirection: Axis.horizontal,
                            children: [
                              ServiceCard(
                                title: 'Ремонт',
                                count: '23000',
                                imageUrl: 'https://picsum.photos/seed/342/600',
                              ),
                            ],
                          ),
                        ),
                        // Main Services Section
                        Padding(
                          padding: EdgeInsets.symmetric(horizontal: 16.0),
                          child: Column(
                            children: [
                              ServiceItem(
                                icon: Icons.people_alt,
                                title: 'Найти специалиста',
                                subtitle: 'Выберите мастера из 1000+',
                                color: theme.primaryColor,
                              ),
                              SizedBox(height: 16.0),
                              ServiceItem(
                                icon: Icons.settings,
                                title: 'Все услуги',
                                subtitle: 'Изучите все категории',
                                color: theme.primaryColor,
                              ),
                              SizedBox(height: 16.0),
                              ServiceItem(
                                icon: Icons.add,
                                title: 'Создать заявку',
                                subtitle: 'Опишите что вам требуется выполнить',
                                color: Color(0xFF2BD375),
                              ),
                            ],
                          ),
                        ),
                        // Top Specialists Section
                        Padding(
                          padding: EdgeInsets.all(16.0),
                          child: Container(
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(11.0),
                              border: Border.all(color: Color(0xFFE2E8F0)),
                            ),
                            child: Padding(
                              padding: EdgeInsets.all(16.0),
                              child: Column(
                                children: [
                                  Row(
                                    children: [
                                      Text(
                                        'Топ специалистов',
                                        style: GoogleFonts.roboto(
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                      Spacer(),
                                      Text(
                                        'Видеть всех',
                                        style: GoogleFonts.inter(
                                          fontSize: 12.0,
                                          fontWeight: FontWeight.normal,
                                        ),
                                      ),
                                      SizedBox(width: 8.0),
                                      Icon(
                                        Icons.arrow_forward,
                                        color: Color(0xFF101828),
                                        size: 14.0,
                                      ),
                                    ],
                                  ),
                                  SizedBox(height: 18.0),
                                  SpecialistCard(),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
