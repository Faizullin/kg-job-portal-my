import 'package:equatable/equatable.dart';
import '../../models/edit_profile_request.dart';

/// События для ProfileBloc
abstract class ProfileEvent extends Equatable {
  const ProfileEvent();

  @override
  List<Object?> get props => [];
}

/// Загрузка профиля пользователя
class LoadProfileEvent extends ProfileEvent {
  const LoadProfileEvent();
}

/// Обновление профиля пользователя
class UpdateProfileEvent extends ProfileEvent {
  final EditProfileRequest request;

  const UpdateProfileEvent(this.request);

  @override
  List<Object?> get props => [request];
}

/// Загрузка аватара
class UploadAvatarEvent extends ProfileEvent {
  final String imagePath;

  const UploadAvatarEvent(this.imagePath);

  @override
  List<Object?> get props => [imagePath];
}

/// Удаление аккаунта
class DeleteAccountEvent extends ProfileEvent {
  const DeleteAccountEvent();
}

/// Открытие модального окна редактирования
class OpenEditModalEvent extends ProfileEvent {
  const OpenEditModalEvent();
}

/// Закрытие модального окна редактирования
class CloseEditModalEvent extends ProfileEvent {
  const CloseEditModalEvent();
}

/// Обновление полей формы редактирования
class UpdateFormFieldEvent extends ProfileEvent {
  final String field;
  final String value;

  const UpdateFormFieldEvent(this.field, this.value);

  @override
  List<Object?> get props => [field, value];
}

/// Валидация формы
class ValidateFormEvent extends ProfileEvent {
  const ValidateFormEvent();
}

/// Очистка ошибок
class ClearErrorsEvent extends ProfileEvent {
  const ClearErrorsEvent();
}
