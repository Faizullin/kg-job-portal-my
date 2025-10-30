import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import '../logic/bloc/home_bloc.dart';
import '../logic/bloc/home_event.dart';

class HomeSearchBar extends StatefulWidget {
  const HomeSearchBar({super.key});

  @override
  State<HomeSearchBar> createState() => _HomeSearchBarState();
}

class _HomeSearchBarState extends State<HomeSearchBar> {
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _searchFocusNode = FocusNode();

  @override
  void dispose() {
    _searchController.dispose();
    _searchFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 60.0,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8.0),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _searchController,
              focusNode: _searchFocusNode,
              textDirection: TextDirection.ltr,
              textAlign: TextAlign.start,
              onChanged: (value) {
                context.read<HomeBloc>().add(SearchEvent(value));
              },
              decoration: InputDecoration(
                hintText: 'Ввести название услуги/сервиса',
                hintStyle: GoogleFonts.roboto(
                  color: Color(0xFF101828),
                  fontWeight: FontWeight.w500,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Colors.white,
                contentPadding: EdgeInsets.symmetric(
                  horizontal: 16.0,
                  vertical: 12.0,
                ),
              ),
              style: GoogleFonts.roboto(
                color: Color(0xFF101828),
              ),
            ),
          ),
          Padding(
            padding: EdgeInsets.only(right: 17.0),
            child: Icon(
              Icons.search_rounded,
              color: Color(0xFF101828),
              size: 24.0,
            ),
          ),
        ],
      ),
    );
  }
}
