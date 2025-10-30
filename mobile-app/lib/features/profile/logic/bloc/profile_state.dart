import 'package:equatable/equatable.dart';
import '../../models/profile_model.dart';
import '../../models/edit_profile_request.dart';

/// Состояния для ProfileBloc
abstract class ProfileState extends Equatable {
  const ProfileState();

  @override
  List<Object?> get props => [];
}

/// Начальное состояние
class ProfileInitialState extends ProfileState {
  const ProfileInitialState();
}

/// Загрузка данных
class ProfileLoadingState extends ProfileState {
  const ProfileLoadingState();
}

/// Профиль успешно загружен
class ProfileLoadedState extends ProfileState {
  final ProfileModel profile;

  const ProfileLoadedState(this.profile);

  @override
  List<Object?> get props => [profile];
}

/// Ошибка загрузки профиля
class ProfileErrorState extends ProfileState {
  final String message;

  const ProfileErrorState(this.message);

  @override
  List<Object?> get props => [message];
}

/// Обновление профиля
class ProfileUpdatingState extends ProfileState {
  final ProfileModel profile;

  const ProfileUpdatingState(this.profile);

  @override
  List<Object?> get props => [profile];
}

/// Профиль успешно обновлен
class ProfileUpdatedState extends ProfileState {
  final ProfileModel profile;
  final String message;

  const ProfileUpdatedState(this.profile, this.message);

  @override
  List<Object?> get props => [profile, message];
}

/// Ошибка обновления профиля
class ProfileUpdateErrorState extends ProfileState {
  final ProfileModel profile;
  final String message;

  const ProfileUpdateErrorState(this.profile, this.message);

  @override
  List<Object?> get props => [profile, message];
}

/// Состояние формы редактирования
class ProfileEditFormState extends ProfileState {
  final ProfileModel profile;
  final EditProfileRequest formData;
  final Map<String, String> errors;
  final bool isModalOpen;
  final bool isValidating;

  const ProfileEditFormState({
    required this.profile,
    required this.formData,
    required this.errors,
    required this.isModalOpen,
    required this.isValidating,
  });

  @override
  List<Object?> get props => [profile, formData, errors, isModalOpen, isValidating];

  ProfileEditFormState copyWith({
    ProfileModel? profile,
    EditProfileRequest? formData,
    Map<String, String>? errors,
    bool? isModalOpen,
    bool? isValidating,
  }) {
    return ProfileEditFormState(
      profile: profile ?? this.profile,
      formData: formData ?? this.formData,
      errors: errors ?? this.errors,
      isModalOpen: isModalOpen ?? this.isModalOpen,
      isValidating: isValidating ?? this.isValidating,
    );
  }
}

/// Загрузка аватара
class ProfileUploadingAvatarState extends ProfileState {
  final ProfileModel profile;

  const ProfileUploadingAvatarState(this.profile);

  @override
  List<Object?> get props => [profile];
}

/// Аватар успешно загружен
class ProfileAvatarUploadedState extends ProfileState {
  final ProfileModel profile;
  final String avatarUrl;

  const ProfileAvatarUploadedState(this.profile, this.avatarUrl);

  @override
  List<Object?> get props => [profile, avatarUrl];
}

/// Ошибка загрузки аватара
class ProfileAvatarUploadErrorState extends ProfileState {
  final ProfileModel profile;
  final String message;

  const ProfileAvatarUploadErrorState(this.profile, this.message);

  @override
  List<Object?> get props => [profile, message];
}

/// Удаление аккаунта
class ProfileDeletingAccountState extends ProfileState {
  const ProfileDeletingAccountState();
}

/// Аккаунт успешно удален
class ProfileAccountDeletedState extends ProfileState {
  const ProfileAccountDeletedState();
}

/// Ошибка удаления аккаунта
class ProfileDeleteAccountErrorState extends ProfileState {
  final String message;

  const ProfileDeleteAccountErrorState(this.message);

  @override
  List<Object?> get props => [message];
}
