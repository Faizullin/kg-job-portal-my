import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:dartz/dartz.dart';
import '../data/profile_repository.dart';
import '../../models/edit_profile_request.dart';
import 'profile_event.dart';
import 'profile_state.dart';

/// BLoC для управления состоянием профиля пользователя
class ProfileBloc extends Bloc<ProfileEvent, ProfileState> {
  final ProfileRepository _repository;

  ProfileBloc({
    required ProfileRepository repository,
  }) : _repository = repository, super(const ProfileInitialState()) {
    
    // Регистрируем обработчики событий
    on<LoadProfileEvent>(_onLoadProfile);
    on<UpdateProfileEvent>(_onUpdateProfile);
    on<UploadAvatarEvent>(_onUploadAvatar);
    on<DeleteAccountEvent>(_onDeleteAccount);
    on<OpenEditModalEvent>(_onOpenEditModal);
    on<CloseEditModalEvent>(_onCloseEditModal);
    on<UpdateFormFieldEvent>(_onUpdateFormField);
    on<ValidateFormEvent>(_onValidateForm);
    on<ClearErrorsEvent>(_onClearErrors);
  }

  /// Загрузка профиля пользователя
  Future<void> _onLoadProfile(
    LoadProfileEvent event,
    Emitter<ProfileState> emit,
  ) async {
    emit(const ProfileLoadingState());

    final result = await _repository.getProfile();
    
    result.fold(
      (error) => emit(ProfileErrorState(error)),
      (profile) => emit(ProfileLoadedState(profile)),
    );
  }

  /// Обновление профиля пользователя
  Future<void> _onUpdateProfile(
    UpdateProfileEvent event,
    Emitter<ProfileState> emit,
  ) async {
    if (state is ProfileLoadedState) {
      final currentProfile = (state as ProfileLoadedState).profile;
      emit(ProfileUpdatingState(currentProfile));

      final result = await _repository.updateProfile(event.request);
      
      result.fold(
        (error) => emit(ProfileUpdateErrorState(currentProfile, error)),
        (response) => emit(ProfileUpdatedState(response.profile, response.message)),
      );
    }
  }

  /// Загрузка аватара
  Future<void> _onUploadAvatar(
    UploadAvatarEvent event,
    Emitter<ProfileState> emit,
  ) async {
    if (state is ProfileLoadedState) {
      final currentProfile = (state as ProfileLoadedState).profile;
      emit(ProfileUploadingAvatarState(currentProfile));

      final result = await _repository.uploadAvatar(event.imagePath);
      
      result.fold(
        (error) => emit(ProfileAvatarUploadErrorState(currentProfile, error)),
        (avatarUrl) {
          final updatedProfile = currentProfile.copyWith(avatarUrl: avatarUrl);
          emit(ProfileAvatarUploadedState(updatedProfile, avatarUrl));
        },
      );
    }
  }

  /// Удаление аккаунта
  Future<void> _onDeleteAccount(
    DeleteAccountEvent event,
    Emitter<ProfileState> emit,
  ) async {
    emit(const ProfileDeletingAccountState());

    final result = await _repository.deleteAccount();
    
    result.fold(
      (error) => emit(ProfileDeleteAccountErrorState(error)),
      (success) => emit(const ProfileAccountDeletedState()),
    );
  }

  /// Открытие модального окна редактирования
  void _onOpenEditModal(
    OpenEditModalEvent event,
    Emitter<ProfileState> emit,
  ) {
    if (state is ProfileLoadedState) {
      final profile = (state as ProfileLoadedState).profile;
      // Разделяем имя на части (простая логика)
      final nameParts = profile.name.trim().split(' ');
      final firstName = nameParts.isNotEmpty ? nameParts.first : '';
      final lastName = nameParts.length > 1 ? nameParts.sublist(1).join(' ') : '';
      
      final formData = EditProfileRequest(
        firstName: firstName,
        lastName: lastName,
        email: profile.email,
        phone: profile.phone,
        city: profile.city,
        gender: profile.gender,
        avatarUrl: profile.avatarUrl,
      );
      
      emit(ProfileEditFormState(
        profile: profile,
        formData: formData,
        errors: {},
        isModalOpen: true,
        isValidating: false,
      ));
    }
  }

  /// Закрытие модального окна редактирования
  void _onCloseEditModal(
    CloseEditModalEvent event,
    Emitter<ProfileState> emit,
  ) {
    if (state is ProfileEditFormState) {
      final profile = (state as ProfileEditFormState).profile;
      emit(ProfileLoadedState(profile));
    }
  }

  /// Обновление полей формы
  void _onUpdateFormField(
    UpdateFormFieldEvent event,
    Emitter<ProfileState> emit,
  ) {
    if (state is ProfileEditFormState) {
      final currentState = state as ProfileEditFormState;
      EditProfileRequest newFormData;
      
      switch (event.field) {
        case 'firstName':
          newFormData = EditProfileRequest(
            firstName: event.value,
            lastName: currentState.formData.lastName,
            email: currentState.formData.email,
            phone: currentState.formData.phone,
            city: currentState.formData.city,
            gender: currentState.formData.gender,
            avatarUrl: currentState.formData.avatarUrl,
          );
          break;
        case 'lastName':
          newFormData = EditProfileRequest(
            firstName: currentState.formData.firstName,
            lastName: event.value,
            email: currentState.formData.email,
            phone: currentState.formData.phone,
            city: currentState.formData.city,
            gender: currentState.formData.gender,
            avatarUrl: currentState.formData.avatarUrl,
          );
          break;
        case 'email':
          newFormData = EditProfileRequest(
            firstName: currentState.formData.firstName,
            lastName: currentState.formData.lastName,
            email: event.value,
            phone: currentState.formData.phone,
            city: currentState.formData.city,
            gender: currentState.formData.gender,
            avatarUrl: currentState.formData.avatarUrl,
          );
          break;
        case 'phone':
          newFormData = EditProfileRequest(
            firstName: currentState.formData.firstName,
            lastName: currentState.formData.lastName,
            email: currentState.formData.email,
            phone: event.value,
            city: currentState.formData.city,
            gender: currentState.formData.gender,
            avatarUrl: currentState.formData.avatarUrl,
          );
          break;
        case 'city':
          newFormData = EditProfileRequest(
            firstName: currentState.formData.firstName,
            lastName: currentState.formData.lastName,
            email: currentState.formData.email,
            phone: currentState.formData.phone,
            city: event.value,
            gender: currentState.formData.gender,
            avatarUrl: currentState.formData.avatarUrl,
          );
          break;
        case 'gender':
          newFormData = EditProfileRequest(
            firstName: currentState.formData.firstName,
            lastName: currentState.formData.lastName,
            email: currentState.formData.email,
            phone: currentState.formData.phone,
            city: currentState.formData.city,
            gender: event.value.isEmpty ? null : event.value,
            avatarUrl: currentState.formData.avatarUrl,
          );
          break;
        default:
          newFormData = currentState.formData;
      }
      
      emit(currentState.copyWith(
        formData: newFormData,
        errors: {}, // Очищаем ошибки при изменении поля
      ));
    }
  }

  /// Валидация формы
  void _onValidateForm(
    ValidateFormEvent event,
    Emitter<ProfileState> emit,
  ) {
    if (state is ProfileEditFormState) {
      final currentState = state as ProfileEditFormState;
      emit(currentState.copyWith(isValidating: true));
      
      final errors = currentState.formData.validate();
      emit(currentState.copyWith(
        errors: errors,
        isValidating: false,
      ));
    }
  }

  /// Очистка ошибок
  void _onClearErrors(
    ClearErrorsEvent event,
    Emitter<ProfileState> emit,
  ) {
    if (state is ProfileEditFormState) {
      final currentState = state as ProfileEditFormState;
      emit(currentState.copyWith(errors: {}));
    }
  }
}
