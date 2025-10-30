import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/master_model.dart';
import 'tell_about_task_screen.dart';

/// Экран подробной информации о мастере
class AboutMasterScreen extends StatelessWidget {
  final MasterModel master;

  const AboutMasterScreen({
    super.key,
    required this.master,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: const Color(0xFF2563EB),
        automaticallyImplyLeading: false,
        elevation: 0.0,
        toolbarHeight: 50.0,
        centerTitle: false,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.white, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        title: Padding(
          padding: const EdgeInsets.only(left: 8.0),
          child: Text(
            'Профиль мастера',
            style: GoogleFonts.inter(
              color: Colors.white,
              fontSize: 18.0,
              fontWeight: FontWeight.w400,
            ),
          ),
        ),
        actions: [
          Row(
            children: [
              IconButton(
                icon: const Icon(Icons.favorite_border,
                    color: Colors.white, size: 21),
                onPressed: () {},
              ),
              IconButton(
                icon:
                    const Icon(Icons.more_vert, color: Colors.white, size: 21),
                onPressed: () {},
              ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // ===== Фиксированная шапка =====
          Container(
            width: double.infinity,
            height: 120,
            color: const Color(0xFF2563EB),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 21, 16, 21),
              child: Container(
                width: double.infinity,
                height: 68.5,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  color: Colors.white,
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        const SizedBox(width: 5),
                        Container(
                          width: 55,
                          height: 55,
                          decoration:
                              const BoxDecoration(shape: BoxShape.circle),
                          child: ClipOval(
                            child: master.avatarUrl != null
                                ? Image.network(
                                    master.avatarUrl!,
                                    fit: BoxFit.cover,
                                    errorBuilder: (context, error, stackTrace) {
                                      return Container(
                                        color: Colors.grey[200],
                                        child: const Icon(Icons.person,
                                            color: Colors.grey, size: 30),
                                      );
                                    },
                                  )
                                : Container(
                                    color: Colors.grey[200],
                                    child: const Icon(Icons.person,
                                        color: Colors.grey, size: 30),
                                  ),
                          ),
                        ),
                        const SizedBox(width: 21),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                master.name,
                                style: GoogleFonts.roboto(
                                  fontWeight: FontWeight.w500,
                                  fontSize: 16,
                                ),
                              ),
                              const SizedBox(height: 3),
                              Text(
                                master.specialty,
                                style: GoogleFonts.inter(
                                  fontSize: 12,
                                  color: const Color(0xFF64748B),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 8),
                        Expanded(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              const SizedBox(height: 8),
                              Container(
                                height: 32,
                                decoration: BoxDecoration(
                                  color: const Color(0xFF2563EB),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    const Icon(Icons.work_outline,
                                        color: Colors.white, size: 16),
                                    const SizedBox(width: 6),
                                    Text(
                                      'Выбрать',
                                      style: GoogleFonts.inter(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w500,
                                        color: Colors.white,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(height: 8),
                              Align(
                                alignment: Alignment.centerRight,
                                child: Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 12, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF2C94C),
                                    borderRadius: BorderRadius.circular(5),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(Icons.star,
                                          color: Colors.white, size: 12),
                                      const SizedBox(width: 4),
                                      Text(
                                        'ТОП мастер',
                                        style: GoogleFonts.inter(
                                          fontSize: 10,
                                          fontWeight: FontWeight.w500,
                                          color: Colors.white,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                              const SizedBox(width: 21),
                            ],
                          ),
                        ),
                        const SizedBox(width: 20),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),

          // ===== Прокручиваемый контент =====
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  // ===== Статистика (перед Примерами работ) =====
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
                    child: _StatsRow(
                      items: const [
                        _StatData(
                            value: '189',
                            label: 'Заказов',
                            color: Color(0xFF00A63E)),
                        _StatData(
                            value: '56',
                            label: 'Отзывов',
                            color: Color(0xFF00A63E)),
                        _StatData(
                            value: '98%',
                            label: 'В срок',
                            color: Color(0xFF155DFC)),
                        _StatData(
                            value: '45%',
                            label: 'Повторно',
                            color: Color(0xFF7C3AED)),
                      ],
                    ),
                  ),
                  const Divider(
                    color: Color(0xFFE2E8F0),
                    thickness: 1,
                    indent: 16,
                    endIndent: 16,
                    height: 24,
                  ),

                  // ===== Контент ниже =====
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Примеры работ',
                          style: GoogleFonts.inter(
                            fontSize: 20,
                            fontWeight: FontWeight.w600,
                            color: const Color(0xFF1A1A1A),
                          ),
                        ),
                        const SizedBox(height: 16),
                        _buildPortfolioGallery(context),
                        const SizedBox(height: 16),
                        _buildSkillsSection(),
                        const SizedBox(height: 24),
                        _buildAboutSpecialistSection(),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(16),
        decoration: const BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Color(0x1A000000),
              offset: Offset(0, -2),
              blurRadius: 8,
            ),
          ],
        ),
        child: SafeArea(
          child: Container(
            width: double.infinity,
            height: 44,
            decoration: BoxDecoration(
              color: const Color(0xFF2563EB),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(8),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const TellAboutTaskScreen(),
                    ),
                  );
                },
                child: Container(
                  alignment: Alignment.center,
                  child: Text(
                    'Рассказать о задаче',
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Галерея портфолио
  Widget _buildPortfolioGallery(BuildContext context) {
    if (master.portfolioImages.isEmpty) {
      return Container(
        height: 158,
        width: 158,
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey[300]!),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.photo_library_outlined,
                  size: 48, color: Colors.grey[400]),
              const SizedBox(height: 8),
              Text(
                'Портфолио пока пусто',
                style: GoogleFonts.inter(fontSize: 14, color: Colors.grey[600]),
              ),
            ],
          ),
        ),
      );
    }

    return SizedBox(
      height: 158,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: master.portfolioImages.length,
        itemBuilder: (context, index) {
          return Container(
            width: 158,
            margin: EdgeInsets.only(
                right: index == master.portfolioImages.length - 1 ? 0 : 12),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: GestureDetector(
                onTap: () =>
                    _showImagePreview(context, master.portfolioImages, index),
                child: Image.network(
                  master.portfolioImages[index],
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) {
                    return Container(
                      color: Colors.grey[200],
                      child: Center(
                        child: Icon(Icons.broken_image,
                            color: Colors.grey[400], size: 32),
                      ),
                    );
                  },
                  loadingBuilder: (context, child, loadingProgress) {
                    if (loadingProgress == null) return child;
                    return Container(
                      color: Colors.grey[200],
                      child: const Center(
                          child: CircularProgressIndicator(strokeWidth: 2)),
                    );
                  },
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  /// Блок "Что умеет" + мини-статистика
  Widget _buildSkillsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Что умеет',
          style: GoogleFonts.inter(
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: const Color(0xFF1A1A1A),
          ),
        ),
        const SizedBox(height: 8),
        if (master.skills.isNotEmpty)
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children:
                master.skills.map((skill) => _buildSkillChip(skill)).toList(),
          ),
        const SizedBox(height: 12),
        const Divider(
          color: Color(0xFFE2E8F0),
          thickness: 1,
          indent: 16,
          endIndent: 16,
          height: 24,
        ),
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                  value: '${master.completedJobs}', label: 'работ'),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildStatCard(value: master.hourlyRate, label: 'за час'),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildStatCard(
                  value: _extractTimeFromResponse(master.responseTime),
                  label: 'скорость ответа'),
            ),
          ],
        ),
        const Divider(
          color: Color(0xFFE2E8F0),
          thickness: 1,
          indent: 16,
          endIndent: 16,
          height: 24,
        ),
        const SizedBox(height: 24),
        _buildReviewsSection(),
      ],
    );
  }

  /// Чип навыка
  Widget _buildSkillChip(String skill) {
    return Container(
      padding: const EdgeInsets.fromLTRB(10, 8, 10, 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
      ),
      child: Text(
        skill,
        style: GoogleFonts.inter(
            fontSize: 12,
            color: const Color(0xFF1A1A1A),
            fontWeight: FontWeight.w500),
      ),
    );
  }

  Widget _buildStatCard({required String value, required String label}) {
    return Column(
      children: [
        Text(
          value,
          style: GoogleFonts.roboto(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF1A1A1A)),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: GoogleFonts.inter(
              fontSize: 12,
              color: const Color(0xFF64748B),
              fontWeight: FontWeight.w400),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  /// Извлекает время из строки ответа (например, "Отвечает за 1 час" -> "час")
  String _extractTimeFromResponse(String responseTime) {
    // Если строка содержит "час", возвращаем просто "час"
    if (responseTime.toLowerCase().contains('час')) {
      return 'час';
    }

    // Если паттерн не найден, возвращаем оригинальную строку
    return responseTime;
  }

  /// Секция отзывов клиентов
  Widget _buildReviewsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Отзывы клиентов',
          style: GoogleFonts.roboto(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: const Color(0xFF1A1A1A),
          ),
        ),
        const SizedBox(height: 16),
        _buildReviewCard(
          name: 'Veronika',
          rating: 4.5,
          review:
              'Lorem ipsum dolor sit amet, consectetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum',
          avatarUrl: 'https://picsum.photos/seed/veronika/150',
        ),
        const SizedBox(height: 16),
        const Divider(
          color: Color(0xFFE2E8F0),
          thickness: 1,
          height: 1,
        ),
        const SizedBox(height: 16),
        _buildReviewCard(
          name: 'Jhonson',
          rating: 4.0,
          review: 'this master is not hepfull...',
          avatarUrl: 'https://picsum.photos/seed/jhonson/150',
        ),
      ],
    );
  }

  /// Карточка отзыва
  Widget _buildReviewCard({
    required String name,
    required double rating,
    required String review,
    required String avatarUrl,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Аватар
        Container(
          width: 50,
          height: 50,
          decoration: const BoxDecoration(shape: BoxShape.circle),
          child: ClipOval(
            child: Image.network(
              avatarUrl,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return Container(
                  color: Colors.grey[200],
                  child: const Icon(Icons.person, color: Colors.grey, size: 25),
                );
              },
            ),
          ),
        ),
        const SizedBox(width: 12),
        // Контент отзыва
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Имя
              Text(
                name,
                style: GoogleFonts.roboto(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: const Color(0xFF1A1A1A),
                ),
              ),
              const SizedBox(height: 4),
              // Рейтинг
              Row(
                children: List.generate(5, (index) {
                  if (index < rating.floor()) {
                    return const Icon(Icons.star,
                        color: Color(0xFFF2C94C), size: 20);
                  } else if (index < rating) {
                    return const Icon(Icons.star_half,
                        color: Color(0xFFF2C94C), size: 20);
                  } else {
                    return const Icon(Icons.star_outline,
                        color: Color(0xFFF2C94C), size: 20);
                  }
                }),
              ),
              const SizedBox(height: 8),
              // Текст отзыва
              Text(
                review,
                style: GoogleFonts.inter(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: const Color(0xFF64748B),
                  height: 1.4,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Секция "О специалисте"
  Widget _buildAboutSpecialistSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Заголовок секции
          Text(
            'О специалисте',
            style: GoogleFonts.roboto(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: const Color(0xFF1A1A1A),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Профессиональная сборка мебели с гарантией качества. Опыт работы 15+ лет с различными брендами: IKEA, Bosch, МДФ. Предоставляю гарантию на все виды работ. Работаю быстро, качественно и аккуратно.',
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.w400,
              color: const Color(0xFF1A1A1A),
              height: 1.5,
            ),
          ),
          const SizedBox(height: 24),
          const Divider(
            color: Color(0xFFE2E8F0),
            thickness: 1,
            indent: 16,
            endIndent: 16,
            height: 24,
          ),
          Text(
            'Профессиональная информация',
            style: GoogleFonts.roboto(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF1A1A1A),
            ),
          ),
          const SizedBox(height: 16),
          _buildInfoRow(
            icon: Icons.work_outline,
            title: 'Опыт работы',
            value: 'С 2009 года',
          ),
          const SizedBox(height: 12),

          // Образование
          _buildInfoRow(
            icon: Icons.school_outlined,
            title: 'Образование',
            value:
                'Кыргызский государственный\nтехнический университет\n(2005–2009)',
          ),
          const SizedBox(height: 12),

          // Языки
          _buildInfoRow(
            assetPath: 'assets/images/language.png',
            title: 'Языки',
            value: 'Русский, Кыргызский, Английский',
          ),
          const SizedBox(height: 24),

          // Сертификаты
          Text(
            'Сертификаты',
            style: GoogleFonts.roboto(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF1A1A1A),
            ),
          ),
          const SizedBox(height: 16),

          // Чипы сертификатов
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildCertificateChip('Certificate 2025'),
              _buildCertificateChip('Certificate 2025'),
              _buildCertificateChip('MEBEL PRO'),
              _buildCertificateChip('Меб'),
              _buildCertificateChip('HELL OUT MEB'),
            ],
          ),
        ],
      ),
    );
  }

  /// Строка информации с иконкой или изображением
  Widget _buildInfoRow({
    IconData? icon,
    String? assetPath,
    required String title,
    required String value,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        SizedBox(
          width: 14,
          height: 14,
          child: assetPath != null
              ? Image.asset(
                  assetPath,
                  width: 14,
                  height: 14,
                  fit: BoxFit.contain,
                  color: const Color(0xFF64748B),
                )
              : Icon(
                  icon!,
                  color: const Color(0xFF64748B),
                  size: 14,
                ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: GoogleFonts.inter(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: const Color(0xFF1A1A1A),
                ),
              ),
              Flexible(
                child: Text(
                  value,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w400,
                    color: const Color(0xFF64748B),
                    height: 1.4,
                  ),
                  textAlign: TextAlign.right,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Чип сертификата
  Widget _buildCertificateChip(String certificate) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
      ),
      child: Text(
        certificate,
        style: GoogleFonts.inter(
          fontSize: 12,
          fontWeight: FontWeight.w400,
          color: const Color(0xFF64748B),
        ),
      ),
    );
  }

  /// Просмотр изображения в диалоге
  void _showImagePreview(
      BuildContext context, List<String> images, int initialIndex) {
    showDialog(
      context: context,
      barrierColor: Colors.black87,
      builder: (context) => Dialog(
        backgroundColor: Colors.transparent,
        child: Stack(
          children: [
            PageView.builder(
              controller: PageController(initialPage: initialIndex),
              itemCount: images.length,
              itemBuilder: (context, index) {
                return Center(
                  child: InteractiveViewer(
                    child: Image.network(
                      images[index],
                      fit: BoxFit.contain,
                      errorBuilder: (context, error, stackTrace) {
                        return Container(
                          color: Colors.grey[800],
                          child: const Center(
                            child: Icon(Icons.broken_image,
                                color: Colors.white, size: 64),
                          ),
                        );
                      },
                    ),
                  ),
                );
              },
            ),
            Positioned(
              top: 40,
              right: 20,
              child: IconButton(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.close, color: Colors.white, size: 30),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// ===== МОДУЛИ СТАТИСТИКИ НАД «ПРИМЕРАМИ РАБОТ» =====

class _StatData {
  final String value;
  final String label;
  final Color color;
  const _StatData(
      {required this.value, required this.label, required this.color});
}

class _StatsRow extends StatelessWidget {
  final List<_StatData> items;
  const _StatsRow({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    final isNarrow = width < 360;

    if (isNarrow) {
      // На узких экранах — 2 колонки, перенос
      return Wrap(
        alignment: WrapAlignment.spaceBetween,
        spacing: 16,
        runSpacing: 12,
        children: items
            .map((e) => SizedBox(
                  width: (width - 16 * 2 - 16) / 2,
                  child: _StatItem(data: e),
                ))
            .toList(),
      );
    }

    // Широкий экран — 4 колонки равномерно
    return Row(
      children: items
          .expand((e) => [
                Expanded(child: _StatItem(data: e)),
                const SizedBox(width: 24),
              ])
          .toList()
        ..removeLast(),
    );
  }
}

class _StatItem extends StatelessWidget {
  final _StatData data;
  const _StatItem({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(
          data.value,
          textAlign: TextAlign.center,
          style: GoogleFonts.inter(
            fontSize: 21, // крупно, как на макете
            fontWeight: FontWeight.w600,
            color: data.color,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          data.label,
          textAlign: TextAlign.center,
          style: GoogleFonts.inter(
            fontSize: 10.5,
            fontWeight: FontWeight.w400,
            color: const Color(0xFF64748B),
          ),
        ),
      ],
    );
  }
}
