import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Экран "Выберите дату и время"
class SelectDateTimeScreen extends StatefulWidget {
  const SelectDateTimeScreen({super.key});

  @override
  State<SelectDateTimeScreen> createState() => _SelectDateTimeScreenState();
}

class _SelectDateTimeScreenState extends State<SelectDateTimeScreen> {
  final _formKey = GlobalKey<FormState>();
  DateTime _selectedDate = DateTime.now();
  int _selectedHour = DateTime.now().hour;
  int _selectedMinute = DateTime.now().minute;
  DateTime _currentMonth = DateTime.now();
  PageController _pageController = PageController();
  bool _showDatePicker = false;
  bool _showTimePicker = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
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
            'Создать заказ',
            style: GoogleFonts.inter(
              color: Colors.white,
              fontSize: 18.0,
              fontWeight: FontWeight.w400,
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: const Color(0xFFE2E8F0),
                      width: 1,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 10,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Заголовок
                      RichText(
                        text: TextSpan(
                          text: 'Выберите дату и время',
                          style: GoogleFonts.roboto(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: const Color(0xFF1A1A1A),
                          ),
                          children: [
                            TextSpan(
                              text: ' *',
                              style: GoogleFonts.inter(
                                color: Colors.red,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Дата
                      Text(
                        'Дата',
                        style: GoogleFonts.roboto(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: const Color(0xFF1A1A1A),
                        ),
                      ),
                      const SizedBox(height: 8),
                      _buildDateField(),
                      
                      // Встроенный календарь
                      if (_showDatePicker) ...[
                        const SizedBox(height: 16),
                        _buildInlineCalendar(),
                      ],
                      
                      const SizedBox(height: 16),

                      // Время
                      Text(
                        'Время',
                        style: GoogleFonts.roboto(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: const Color(0xFF1A1A1A),
                        ),
                      ),
                      const SizedBox(height: 8),
                      _buildTimeField(),
                      
                      // Встроенный time picker
                      if (_showTimePicker) ...[
                        const SizedBox(height: 16),
                        _buildInlineTimePicker(),
                      ],
                    ],
                  ),
                ),
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
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Заказ успешно создан!'),
                      backgroundColor: Colors.green,
                    ),
                  );
                },
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Продолжить',
                      style: GoogleFonts.inter(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Icon(
                      Icons.arrow_back,
                      color: Colors.white,
                      size: 18,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Поле выбора даты
  Widget _buildDateField() {
    return GestureDetector(
      onTap: () {
        setState(() {
          _showDatePicker = !_showDatePicker;
          _showTimePicker = false;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: _showDatePicker ? const Color(0xFF58A8F2) : const Color(0xFFE2E8F0),
            width: _showDatePicker ? 2 : 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${_selectedDate.day.toString().padLeft(2, '0')}.${_selectedDate.month.toString().padLeft(2, '0')}.${_selectedDate.year}',
              style: GoogleFonts.inter(
                fontSize: 14,
                color: const Color(0xFF58A8F2),
              ),
            ),
            Icon(
              _showDatePicker ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
              color: const Color(0xFF94A3B8),
            ),
          ],
        ),
      ),
    );
  }

  /// Поле выбора времени
  Widget _buildTimeField() {
    return GestureDetector(
      onTap: () {
        setState(() {
          _showTimePicker = !_showTimePicker;
          _showDatePicker = false;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: _showTimePicker ? const Color(0xFF58A8F2) : const Color(0xFFE2E8F0),
            width: _showTimePicker ? 2 : 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${_selectedHour.toString().padLeft(2, '0')}:${_selectedMinute.toString().padLeft(2, '0')}',
              style: GoogleFonts.inter(
                fontSize: 14,
                color: const Color(0xFF1A1A1A),
              ),
            ),
            Icon(
              _showTimePicker ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
              color: const Color(0xFF94A3B8),
            ),
          ],
        ),
      ),
    );
  }

  /// Встроенный календарь
  Widget _buildInlineCalendar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        children: [
          // Заголовок с месяцем и навигацией
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              IconButton(
                onPressed: () {
                  setState(() {
                    _currentMonth = DateTime(_currentMonth.year, _currentMonth.month - 1);
                  });
                },
                icon: const Icon(Icons.chevron_left, color: Color(0xFF64748B)),
              ),
              Text(
                _getMonthName(_currentMonth.month),
                style: GoogleFonts.inter(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: const Color(0xFF1A1A1A),
                ),
              ),
              IconButton(
                onPressed: () {
                  setState(() {
                    _currentMonth = DateTime(_currentMonth.year, _currentMonth.month + 1);
                  });
                },
                icon: const Icon(Icons.chevron_right, color: Color(0xFF64748B)),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Дни недели
          Row(
            children: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                .map((day) => Expanded(
                      child: Center(
                        child: Text(
                          day,
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            color: day == 'Sun' || day == 'Sat' 
                                ? Colors.red 
                                : const Color(0xFF64748B),
                          ),
                        ),
                      ),
                    ))
                .toList(),
          ),
          const SizedBox(height: 8),
          
          // Календарная сетка
          _buildCalendarGrid(),
        ],
      ),
    );
  }

  /// Встроенный time picker
  Widget _buildInlineTimePicker() {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          // Часы
          Expanded(
            child: _buildScrollablePicker(
              itemCount: 24,
              selectedIndex: _selectedHour,
              onSelectedItemChanged: (index) {
                setState(() {
                  _selectedHour = index;
                });
              },
              itemBuilder: (index) => index.toString().padLeft(2, '0'),
            ),
          ),
          
          // Двоеточие
          Container(
            width: 30,
            child: Center(
              child: Text(
                ':',
                style: GoogleFonts.inter(
                  fontSize: 32,
                  fontWeight: FontWeight.w600,
                  color: const Color(0xFF1A1A1A),
                ),
              ),
            ),
          ),
          
          // Минуты
          Expanded(
            child: _buildScrollablePicker(
              itemCount: 60,
              selectedIndex: _selectedMinute,
              onSelectedItemChanged: (index) {
                setState(() {
                  _selectedMinute = index;
                });
              },
              itemBuilder: (index) => index.toString().padLeft(2, '0'),
            ),
          ),
        ],
      ),
    );
  }

  /// Прокручиваемый пикер
  Widget _buildScrollablePicker({
    required int itemCount,
    required int selectedIndex,
    required ValueChanged<int> onSelectedItemChanged,
    required String Function(int) itemBuilder,
  }) {
    return Container(
      height: 150,
      child: Stack(
        children: [
          // Центральная подсветка
          Center(
            child: Container(
              height: 40,
              decoration: BoxDecoration(
                color: const Color(0xFF58A8F2).withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: const Color(0xFF58A8F2).withOpacity(0.3),
                  width: 1,
                ),
              ),
            ),
          ),
          
          // Прокручиваемый список
          ListWheelScrollView.useDelegate(
            controller: FixedExtentScrollController(
              initialItem: selectedIndex,
            ),
            itemExtent: 40,
            perspective: 0.005,
            diameterRatio: 1.2,
            physics: const FixedExtentScrollPhysics(),
            onSelectedItemChanged: onSelectedItemChanged,
            childDelegate: ListWheelChildBuilderDelegate(
              childCount: itemCount,
              builder: (context, index) {
                final isSelected = index == selectedIndex;
                return Container(
                  height: 40,
                  child: Center(
                    child: Text(
                      itemBuilder(index),
                      style: GoogleFonts.inter(
                        fontSize: isSelected ? 24 : 18,
                        fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                        color: isSelected 
                            ? const Color(0xFF58A8F2)
                            : const Color(0xFF64748B),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  /// Кнопки для изменения времени
  Widget _buildTimeButton(String text, VoidCallback onPressed) {
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        width: 30,
        height: 30,
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Center(
          child: Text(
            text,
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF1A1A1A),
            ),
          ),
        ),
      ),
    );
  }

  /// Сетка календаря
  Widget _buildCalendarGrid() {
    final firstDayOfMonth = DateTime(_currentMonth.year, _currentMonth.month, 1);
    final lastDayOfMonth = DateTime(_currentMonth.year, _currentMonth.month + 1, 0);
    final firstWeekday = firstDayOfMonth.weekday % 7;
    final daysInMonth = lastDayOfMonth.day;

    List<Widget> dayWidgets = [];

    // Пустые ячейки для начала месяца
    for (int i = 0; i < firstWeekday; i++) {
      dayWidgets.add(const SizedBox());
    }

    // Дни месяца
    for (int day = 1; day <= daysInMonth; day++) {
      final date = DateTime(_currentMonth.year, _currentMonth.month, day);
      final isSelected = date.day == _selectedDate.day &&
          date.month == _selectedDate.month &&
          date.year == _selectedDate.year;
      final isToday = date.day == DateTime.now().day &&
          date.month == DateTime.now().month &&
          date.year == DateTime.now().year;

      dayWidgets.add(
        GestureDetector(
          onTap: () {
            setState(() {
              _selectedDate = date;
            });
          },
          child: Container(
            margin: const EdgeInsets.all(2),
            decoration: BoxDecoration(
              color: isSelected ? const Color(0xFF58A8F2) : null,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Center(
              child: Text(
                day.toString(),
                style: GoogleFonts.inter(
                  fontSize: 14,
                  fontWeight: isToday ? FontWeight.w600 : FontWeight.w400,
                  color: isSelected
                      ? Colors.white
                      : isToday
                          ? const Color(0xFF58A8F2)
                          : const Color(0xFF1A1A1A),
                ),
              ),
            ),
          ),
        ),
      );
    }

    return GridView.count(
      crossAxisCount: 7,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      children: dayWidgets,
    );
  }

  /// Получить название месяца
  String _getMonthName(int month) {
    const months = [
      '', 'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return months[month];
  }
}
