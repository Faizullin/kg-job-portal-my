/// Модель запроса на редактирование профиля
class EditProfileRequest {
  final String firstName;
  final String lastName;
  final String email;
  final String phone;
  final String city;
  final String? gender;
  final String? avatarUrl;

  const EditProfileRequest({
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.phone,
    required this.city,
    this.gender,
    this.avatarUrl,
  });

  /// Копирование с изменениями
  EditProfileRequest copyWith({
    String? firstName,
    String? lastName,
    String? email,
    String? phone,
    String? city,
    String? gender,
    String? avatarUrl,
  }) {
    return EditProfileRequest(
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      city: city ?? this.city,
      gender: gender ?? this.gender,
      avatarUrl: avatarUrl ?? this.avatarUrl,
    );
  }

  /// Валидация данных формы
  Map<String, String> validate() {
    final errors = <String, String>{};

    if (firstName.trim().isEmpty) {
      errors['firstName'] = 'Имя обязательно для заполнения';
    }

    if (lastName.trim().isEmpty) {
      errors['lastName'] = 'Фамилия обязательна для заполнения';
    }

    if (email.trim().isEmpty) {
      errors['email'] = 'Email обязателен для заполнения';
    } else if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(email)) {
      errors['email'] = 'Введите корректный email';
    }

    if (phone.trim().isEmpty) {
      errors['phone'] = 'Номер телефона обязателен для заполнения';
    } else if (phone.length < 10) {
      errors['phone'] = 'Номер телефона должен содержать минимум 10 цифр';
    }

    if (city.trim().isEmpty) {
      errors['city'] = 'Город обязателен для заполнения';
    }

    return errors;
  }

  @override
  String toString() {
    return 'EditProfileRequest(firstName: $firstName, lastName: $lastName, email: $email, phone: $phone, city: $city, gender: $gender, avatarUrl: $avatarUrl)';
  }
}